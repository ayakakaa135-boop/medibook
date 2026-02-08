from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal
import json

from .models import Appointment, Payment, PaymentCard
from .forms import PaymentForm, SavedCardPaymentForm


# This would integrate with actual payment gateway
# For now, it's a mock implementation
class PaymentGateway:
    """Mock payment gateway - replace with actual gateway (Stripe, PayTabs, etc.)"""

    @staticmethod
    def process_payment(card_data, amount, currency='SAR'):
        """
        Process payment through gateway

        Args:
            card_data: Dict with card details
            amount: Payment amount
            currency: Currency code

        Returns:
            Dict with transaction result
        """
        # In production, integrate with actual payment gateway
        # Example: Stripe, PayTabs, Checkout.com, etc.

        try:
            # Simulate payment processing
            import time
            time.sleep(1)  # Simulate network delay

            # Mock successful transaction
            transaction_id = f"TXN-{timezone.now().strftime('%Y%m%d%H%M%S')}"

            return {
                'success': True,
                'transaction_id': transaction_id,
                'amount': float(amount),
                'currency': currency,
                'card_brand': PaymentGateway._detect_card_brand(card_data['card_number']),
                'card_last_four': card_data['card_number'][-4:],
                'message': 'Payment successful'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Payment failed'
            }

    @staticmethod
    def _detect_card_brand(card_number):
        """Detect card brand from card number"""
        card_number = card_number.replace(' ', '').replace('-', '')

        if card_number[0] == '4':
            return 'visa'
        elif card_number[:2] in ['51', '52', '53', '54', '55']:
            return 'mastercard'
        elif card_number[:2] in ['34', '37']:
            return 'amex'
        else:
            return 'unknown'

    @staticmethod
    def tokenize_card(card_data):
        """
        Tokenize card for future use

        Returns:
            String token
        """
        # In production, use gateway's tokenization
        import hashlib
        token_string = f"{card_data['card_number']}{card_data['expiry_month']}{card_data['expiry_year']}"
        return hashlib.sha256(token_string.encode()).hexdigest()

    @staticmethod
    def process_refund(transaction_id, amount):
        """Process refund"""
        try:
            # Simulate refund processing
            return {
                'success': True,
                'refund_id': f"REF-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                'amount': float(amount),
                'message': 'Refund successful'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Refund failed'
            }


class AppointmentPaymentView(LoginRequiredMixin, CreateView):
    """Payment view for appointment"""

    model = Payment
    form_class = PaymentForm
    template_name = 'appointments/payment.html'

    def dispatch(self, request, *args, **kwargs):
        """Get appointment and check permissions"""
        self.appointment = get_object_or_404(
            Appointment,
            pk=kwargs.get('appointment_id'),
            patient=request.user
        )

        # Check if already paid
        if self.appointment.is_paid:
            messages.info(request, _('This appointment is already paid'))
            return redirect(self.appointment.get_absolute_url())

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointment'] = self.appointment

        # Calculate amounts
        context['base_amount'] = self.appointment.base_price
        context['late_fee'] = self.appointment.late_payment_fee
        context['total_amount'] = self.appointment.total_amount
        context['is_overdue'] = self.appointment.is_payment_overdue
        context['days_until_due'] = self.appointment.days_until_payment_due

        # Get saved cards
        context['saved_cards'] = PaymentCard.objects.filter(
            patient=self.request.user,
            is_active=True
        )

        return context

    def form_invalid(self, form):
        """Handle invalid form submission"""
        print("Payment Form Errors:", form.errors)
        if form.non_field_errors():
            print("Non-field errors:", form.non_field_errors())

        messages.error(self.request, _('Please correct the errors below'))
        return super().form_invalid(form)

    def form_valid(self, form):
        """Process payment - FIXED VERSION"""
        print("✅ Form is valid, processing payment...")  # للتشخيص

        try:
            with transaction.atomic():
                # ✅ إنشاء سجل الدفع يدوياً بدلاً من form.save()
                payment = Payment.objects.create(
                    appointment=self.appointment,
                    patient=self.request.user,
                    amount=self.appointment.total_amount,
                    base_amount=self.appointment.base_price,
                    late_fee_amount=self.appointment.late_payment_fee,
                    status=Payment.PaymentStatus.PROCESSING,
                    payment_method=Payment.PaymentMethod.VISA  # سيتم تحديثه بناءً على نوع البطاقة
                )
                print(f"✅ Payment record created: {payment.id}")

                # Prepare card data
                card_data = {
                    'card_number': form.cleaned_data['card_number'],
                    'cardholder_name': form.cleaned_data['cardholder_name'],
                    'expiry_month': form.cleaned_data['expiry_month'],
                    'expiry_year': form.cleaned_data['expiry_year'],
                    'cvv': form.cleaned_data['cvv']
                }
                print(f"✅ Card data prepared")

                # Process payment through gateway
                result = PaymentGateway.process_payment(
                    card_data,
                    payment.amount,
                    currency='SAR'
                )
                print(f"✅ Gateway response: {result}")

                if result['success']:
                    # Update payment
                    payment.transaction_id = result['transaction_id']
                    payment.card_last_four = result['card_last_four']
                    payment.card_brand = result['card_brand']

                    # ✅ تحديث payment_method بناءً على نوع البطاقة
                    if result['card_brand'] == 'visa':
                        payment.payment_method = Payment.PaymentMethod.VISA
                    elif result['card_brand'] == 'mastercard':
                        payment.payment_method = Payment.PaymentMethod.MASTERCARD

                    payment.gateway_response = result
                    payment.mark_as_completed()
                    print(f"✅ Payment completed: {payment.transaction_id}")

                    # Save card if requested
                    if form.cleaned_data.get('save_card'):
                        card_token = PaymentGateway.tokenize_card(card_data)
                        PaymentCard.objects.create(
                            patient=self.request.user,
                            card_token=card_token,
                            card_last_four=result['card_last_four'],
                            card_brand=result['card_brand'],
                            expiry_month=card_data['expiry_month'],
                            expiry_year=card_data['expiry_year'],
                            cardholder_name=card_data['cardholder_name']
                        )
                        print(f"✅ Card saved")

                    messages.success(
                        self.request,
                        _('Payment successful! Transaction ID: %(transaction_id)s') % {
                            'transaction_id': payment.transaction_id
                        }
                    )

                    print(f"✅ Redirecting to success page...")
                    return redirect('appointments:payment_success', payment_id=payment.pk)

                else:
                    # Payment failed
                    print(f"❌ Payment failed: {result.get('message')}")
                    payment.mark_as_failed(result.get('error', 'Unknown error'))
                    messages.error(
                        self.request,
                        _('Payment failed: %(error)s') % {'error': result.get('message', 'Unknown error')}
                    )
                    return self.form_invalid(form)

        except Exception as e:
            print(f"❌ Payment processing error: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(self.request, _('An error occurred during payment processing'))
            return self.form_invalid(form)

    def get_success_url(self):
        """Return success URL"""
        return reverse('appointments:payment_success', kwargs={'payment_id': self.object.pk})


@login_required
def pay_with_saved_card(request, appointment_id, card_id):
    """Pay using saved card"""
    appointment = get_object_or_404(
        Appointment,
        pk=appointment_id,
        patient=request.user
    )

    if appointment.is_paid:
        messages.info(request, _('This appointment is already paid'))
        return redirect(appointment.get_absolute_url())

    card = get_object_or_404(
        PaymentCard,
        pk=card_id,
        patient=request.user,
        is_active=True
    )

    if request.method == 'POST':
        cvv = request.POST.get('cvv')

        # Validate CVV
        if not cvv or not cvv.isdigit() or not (3 <= len(cvv) <= 4):
            messages.error(request, _('Invalid CVV'))
            return redirect('appointments:payment', appointment_id=appointment.pk)

        try:
            with transaction.atomic():
                # Create payment record
                payment = Payment.objects.create(
                    appointment=appointment,
                    patient=request.user,
                    amount=appointment.total_amount,
                    base_amount=appointment.base_price,
                    late_fee_amount=appointment.late_payment_fee,
                    status=Payment.PaymentStatus.PROCESSING,
                    card_last_four=card.card_last_four,
                    card_brand=card.card_brand,
                    payment_method=Payment.PaymentMethod.VISA if card.card_brand == 'visa' else Payment.PaymentMethod.MASTERCARD
                )

                # Process payment (mock)
                card_data = {
                    'card_number': f"************{card.card_last_four}",
                    'cvv': cvv
                }

                result = PaymentGateway.process_payment(
                    card_data,
                    payment.amount,
                    currency='SAR'
                )

                if result['success']:
                    payment.transaction_id = result['transaction_id']
                    payment.gateway_response = result
                    payment.mark_as_completed()

                    messages.success(
                        request,
                        _('Payment successful!')
                    )
                    return redirect('appointments:payment_success', payment_id=payment.pk)
                else:
                    payment.mark_as_failed(result.get('error'))
                    messages.error(request, _('Payment failed'))
                    return redirect('appointments:payment', appointment_id=appointment.pk)

        except Exception as e:
            messages.error(request, _('An error occurred during payment'))
            return redirect('appointments:payment', appointment_id=appointment.pk)

    return render(request, 'appointments/saved_card_payment.html', {
        'appointment': appointment,
        'card': card
    })


class PaymentSuccessView(LoginRequiredMixin, DetailView):
    """Payment success confirmation"""

    model = Payment
    template_name = 'appointments/payment_success.html'
    context_object_name = 'payment'
    pk_url_kwarg = 'payment_id'

    def get_queryset(self):
        return Payment.objects.filter(patient=self.request.user)


class PaymentHistoryView(LoginRequiredMixin, ListView):
    """Payment history for patient"""

    model = Payment
    template_name = 'appointments/payment_history.html'
    context_object_name = 'payments'
    paginate_by = 20

    def get_queryset(self):
        return Payment.objects.filter(
            patient=self.request.user
        ).select_related(
            'appointment__doctor__user',
            'appointment__service'
        ).order_by('-created_at')


@login_required
def check_payment_status(request, appointment_id):
    """AJAX endpoint to check payment status"""
    appointment = get_object_or_404(
        Appointment,
        pk=appointment_id,
        patient=request.user
    )

    # Update late payment fee if overdue
    if appointment.is_payment_overdue and not appointment.is_paid:
        late_fee = appointment.calculate_late_payment_fee()
        if late_fee > appointment.late_payment_fee:
            appointment.late_payment_fee = late_fee
            appointment.save()

    return JsonResponse({
        'is_paid': appointment.is_paid,
        'is_overdue': appointment.is_payment_overdue,
        'days_until_due': appointment.days_until_payment_due,
        'base_amount': float(appointment.base_price),
        'late_fee': float(appointment.late_payment_fee),
        'total_amount': float(appointment.total_amount),
        'payment_due_date': appointment.payment_due_date.isoformat() if appointment.payment_due_date else None
    })


@login_required
def cancel_appointment_with_fee(request, pk):
    """Cancel appointment with potential fee"""
    appointment = get_object_or_404(
        Appointment,
        pk=pk,
        patient=request.user
    )

    if not appointment.can_cancel:
        messages.error(request, _('This appointment cannot be canceled'))
        return redirect(appointment.get_absolute_url())

    # Calculate cancellation fee
    hours_until = appointment.hours_until_appointment
    will_charge_fee = hours_until is not None and hours_until < 24
    cancellation_fee = Decimal('0.00')

    if will_charge_fee:
        cancellation_fee = appointment.calculate_cancellation_fee()

    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        acknowledge = request.POST.get('acknowledge_fee')

        if will_charge_fee and not acknowledge:
            messages.error(request, _('You must acknowledge the cancellation fee'))
            return redirect('appointments:cancel_with_fee', pk=pk)

        try:
            with transaction.atomic():
                # Apply cancellation fee
                if will_charge_fee:
                    appointment.cancellation_fee = cancellation_fee
                    appointment.total_amount = appointment.base_price + appointment.cancellation_fee + appointment.late_payment_fee

                    # If not paid yet, add fee to total
                    if not appointment.is_paid:
                        appointment.save()
                    else:
                        # If already paid, need to process refund minus fee
                        refund_amount = appointment.base_price - cancellation_fee

                        # Find the payment
                        payment = appointment.payments.filter(
                            status=Payment.PaymentStatus.COMPLETED
                        ).first()

                        if payment and refund_amount > 0:
                            # Process refund
                            result = PaymentGateway.process_refund(
                                payment.transaction_id,
                                refund_amount
                            )

                            if result['success']:
                                payment.is_refunded = True
                                payment.refund_amount = refund_amount
                                payment.refunded_at = timezone.now()
                                payment.refund_reason = f'Cancellation fee applied: {cancellation_fee} SAR'
                                payment.save()

                # Cancel appointment
                appointment.status = Appointment.Status.CANCELED
                appointment.canceled_at = timezone.now()
                appointment.cancellation_reason = reason
                appointment.save()

                if will_charge_fee:
                    messages.warning(
                        request,
                        _('Appointment canceled. Cancellation fee: %(fee)s SAR') % {
                            'fee': cancellation_fee
                        }
                    )
                else:
                    messages.success(request, _('Appointment canceled successfully'))

                return redirect('appointments:my_appointments')

        except Exception as e:
            print(f"Cancellation error: {str(e)}")
            messages.error(request, _('An error occurred during cancellation'))
            return redirect(appointment.get_absolute_url())

    return render(request, 'appointments/cancel_with_fee.html', {
        'appointment': appointment,
        'hours_until': hours_until,
        'will_charge_fee': will_charge_fee,
        'cancellation_fee': cancellation_fee,
        'can_cancel_free': appointment.can_cancel_free
    })


@login_required
def manage_payment_cards(request):
    """Manage saved payment cards"""
    cards = PaymentCard.objects.filter(
        patient=request.user,
        is_active=True
    ).order_by('-is_default', '-created_at')

    return render(request, 'appointments/manage_cards.html', {
        'cards': cards
    })


@login_required
def delete_payment_card(request, card_id):
    """Delete saved payment card"""
    card = get_object_or_404(
        PaymentCard,
        pk=card_id,
        patient=request.user
    )

    if request.method == 'POST':
        card.is_active = False
        card.save()
        messages.success(request, _('Card removed successfully'))

    return redirect('appointments:manage_cards')


@login_required
def set_default_card(request, card_id):
    """Set card as default"""
    card = get_object_or_404(
        PaymentCard,
        pk=card_id,
        patient=request.user,
        is_active=True
    )

    if request.method == 'POST':
        card.is_default = True
        card.save()
        messages.success(request, _('Default card updated'))

    return redirect('appointments:manage_cards')