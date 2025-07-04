'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Navigation } from '@/components/navigation';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { Cart, CartSummary } from '@/types';
import { ArrowLeft, CreditCard, Truck, CheckCircle } from 'lucide-react';

export default function CheckoutPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [cart, setCart] = useState<Cart | null>(null);
  const [summary, setSummary] = useState<CartSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [formData, setFormData] = useState({
    shipping_address: '',
    payment_method: 'credit_card',
    notes: ''
  });

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }

    loadCart();
  }, [user, router]);

  const loadCart = async () => {
    try {
      setLoading(true);
      const [cartData, summaryData] = await Promise.all([
        api.getCart(),
        api.getCartSummary()
      ]);
      
      setCart(cartData);
      setSummary(summaryData);

      if (cartData.items.length === 0) {
        router.push('/cart');
        return;
      }
    } catch (error) {
      console.error('Failed to load cart:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!summary || summary.total === 0) {
      alert('Cart is empty');
      return;
    }

    setCheckoutLoading(true);
    try {
      const order = await api.checkoutCart({
        shipping_address: formData.shipping_address,
        payment_method: formData.payment_method,
        notes: formData.notes
      });

      // Track checkout event
      await api.trackEvent({
        event_type: 'checkout_completed',
        customer_id: user!.id,
        session_id: 'session_' + Date.now(),
        properties: {
          order_id: order.order_id,
          total_amount: summary.total,
          items_count: summary.quantity
        }
      });

      alert('Order placed successfully!');
      router.push(`/orders/${order.order_id}`);
    } catch (error) {
      console.error('Checkout failed:', error);
      alert('Checkout failed. Please try again.');
    } finally {
      setCheckoutLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center py-12">
            <CheckCircle className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">Your cart is empty</h2>
            <p className="text-gray-600 mb-6">Add some items to your cart before checkout.</p>
            <button
              onClick={() => router.push('/')}
              className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 transition-colors"
            >
              Continue Shopping
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <button
            onClick={() => router.push('/cart')}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Cart
          </button>
        </div>

        <h1 className="text-3xl font-bold text-gray-900 mb-8">Checkout</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Checkout Form */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Order Information</h2>
              
              <form onSubmit={handleCheckout} className="space-y-6">
                {/* Shipping Address */}
                <div>
                  <label htmlFor="shipping_address" className="block text-sm font-medium text-gray-700 mb-2">
                    Shipping Address *
                  </label>
                  <textarea
                    id="shipping_address"
                    name="shipping_address"
                    value={formData.shipping_address}
                    onChange={handleInputChange}
                    required
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter your complete shipping address"
                  />
                </div>

                {/* Payment Method */}
                <div>
                  <label htmlFor="payment_method" className="block text-sm font-medium text-gray-700 mb-2">
                    Payment Method *
                  </label>
                  <select
                    id="payment_method"
                    name="payment_method"
                    value={formData.payment_method}
                    onChange={handleInputChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="credit_card">Credit Card</option>
                    <option value="debit_card">Debit Card</option>
                    <option value="paypal">PayPal</option>
                    <option value="bank_transfer">Bank Transfer</option>
                  </select>
                </div>

                {/* Order Notes */}
                <div>
                  <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
                    Order Notes (Optional)
                  </label>
                  <textarea
                    id="notes"
                    name="notes"
                    value={formData.notes}
                    onChange={handleInputChange}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Any special instructions or notes for your order"
                  />
                </div>

                <button
                  type="submit"
                  disabled={checkoutLoading}
                  className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
                >
                  {checkoutLoading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  ) : (
                    <>
                      <CreditCard className="h-5 w-5 mr-2" />
                      Place Order
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Order Summary</h2>
              
              <div className="space-y-4 mb-6">
                <div className="flex justify-between">
                  <span className="text-gray-600">Items ({summary?.quantity || 0})</span>
                  <span className="font-medium">${summary?.total.toFixed(2) || '0.00'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Shipping</span>
                  <span className="font-medium text-green-600">Free</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Tax</span>
                  <span className="font-medium">$0.00</span>
                </div>
                <div className="border-t pt-4">
                  <div className="flex justify-between">
                    <span className="text-lg font-semibold">Total</span>
                    <span className="text-lg font-semibold text-blue-600">
                      ${summary?.total.toFixed(2) || '0.00'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Order Items Preview */}
              <div className="border-t pt-4">
                <h3 className="font-medium text-gray-900 mb-3">Order Items</h3>
                <div className="space-y-2">
                  {cart.items.slice(0, 3).map((item, index) => (
                    <div key={index} className="flex justify-between text-sm">
                      <span className="text-gray-600">
                        {item.quantity}x Item #{item.product_id.slice(-4)}
                      </span>
                      <span className="font-medium">-</span>
                    </div>
                  ))}
                  {cart.items.length > 3 && (
                    <div className="text-sm text-gray-500">
                      +{cart.items.length - 3} more items
                    </div>
                  )}
                </div>
              </div>

              <div className="mt-6 p-4 bg-blue-50 rounded-md">
                <div className="flex items-center">
                  <Truck className="h-5 w-5 text-blue-600 mr-2" />
                  <div>
                    <p className="text-sm font-medium text-blue-900">Free Shipping</p>
                    <p className="text-xs text-blue-700">Estimated delivery: 3-5 business days</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 