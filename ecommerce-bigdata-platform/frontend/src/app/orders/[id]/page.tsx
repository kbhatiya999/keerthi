'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Navigation } from '@/components/navigation';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';
import { Order } from '@/types';
import { ArrowLeft, Package, Calendar, MapPin, CreditCard, Truck, Edit, Save } from 'lucide-react';

export default function OrderDetailPage() {
  const { user } = useAuth();
  const router = useRouter();
  const params = useParams();
  const orderId = params.id as string;
  
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [statusUpdate, setStatusUpdate] = useState({
    status: '',
    payment_status: ''
  });

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }

    if (orderId) {
      loadOrder();
    }
  }, [user, router, orderId]);

  const loadOrder = async () => {
    try {
      setLoading(true);
      const orderData = await api.getOrder(orderId);
      setOrder(orderData);
      setStatusUpdate({
        status: orderData.status,
        payment_status: orderData.payment_status
      });
    } catch (error) {
      console.error('Failed to fetch order:', error);
      alert('Order not found');
      router.push('/orders');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async () => {
    if (!order) return;
    
    setSaving(true);
    try {
      await api.updateOrder(orderId, statusUpdate);
      await loadOrder(); // Reload order to get updated data
      setEditing(false);
      alert('Order status updated successfully!');
    } catch (error) {
      console.error('Failed to update order status:', error);
      alert('Failed to update order status');
    } finally {
      setSaving(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'confirmed':
        return 'bg-blue-100 text-blue-800';
      case 'shipped':
        return 'bg-purple-100 text-purple-800';
      case 'delivered':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPaymentStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'refunded':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const isAdmin = user && (user.role === 'admin' || user.role === 'super_admin');

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

  if (!order) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center py-12">
            <Package className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">Order not found</h2>
            <p className="text-gray-600 mb-6">The order you're looking for doesn't exist.</p>
            <button
              onClick={() => router.push('/orders')}
              className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 transition-colors"
            >
              Back to Orders
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
            onClick={() => router.push('/orders')}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Orders
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Order #{order.id.slice(-8)}
              </h1>
              <p className="text-gray-600">
                Placed on {new Date(order.created_at).toLocaleDateString()}
              </p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-gray-900">
                ${order.total_amount.toFixed(2)}
              </p>
              <p className="text-sm text-gray-500">
                {order.items.length} item{order.items.length !== 1 ? 's' : ''}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-gray-900">Order Status</h3>
                {isAdmin && (
                  <button
                    onClick={() => setEditing(!editing)}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    {editing ? 'Cancel' : <Edit className="h-4 w-4" />}
                  </button>
                )}
              </div>
              
              {editing && isAdmin ? (
                <div className="space-y-2">
                  <select
                    value={statusUpdate.status}
                    onChange={(e) => setStatusUpdate(prev => ({ ...prev, status: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="pending">Pending</option>
                    <option value="confirmed">Confirmed</option>
                    <option value="shipped">Shipped</option>
                    <option value="delivered">Delivered</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                  <button
                    onClick={handleStatusUpdate}
                    disabled={saving}
                    className="flex items-center px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:bg-gray-400"
                  >
                    {saving ? (
                      <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1"></div>
                    ) : (
                      <Save className="h-3 w-3 mr-1" />
                    )}
                    {saving ? 'Saving...' : 'Save'}
                  </button>
                </div>
              ) : (
                <span className={`inline-flex px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(order.status)}`}>
                  {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                </span>
              )}
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-gray-900">Payment Status</h3>
              </div>
              
              {editing && isAdmin ? (
                <div className="space-y-2">
                  <select
                    value={statusUpdate.payment_status}
                    onChange={(e) => setStatusUpdate(prev => ({ ...prev, payment_status: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="pending">Pending</option>
                    <option value="completed">Completed</option>
                    <option value="failed">Failed</option>
                    <option value="refunded">Refunded</option>
                  </select>
                </div>
              ) : (
                <span className={`inline-flex px-3 py-1 text-sm font-medium rounded-full ${getPaymentStatusColor(order.payment_status)}`}>
                  {order.payment_status.charAt(0).toUpperCase() + order.payment_status.slice(1)}
                </span>
              )}
            </div>
          </div>

          {isAdmin && (
            <div className="mb-6 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">Admin Actions</h4>
              <p className="text-sm text-blue-700">
                Click the edit icon next to Order Status to update the order status. 
                This will notify the customer of the status change.
              </p>
            </div>
          )}

          <div className="border-t pt-6">
            <h3 className="font-semibold text-gray-900 mb-4">Order Items</h3>
            <div className="space-y-4">
              {order.items.map((item, index) => (
                <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">
                      {item.product_name || `Product #${item.product_id.slice(-4)}`}
                    </h4>
                    <p className="text-sm text-gray-500">
                      Quantity: {item.quantity}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">
                      ${(item.price * item.quantity).toFixed(2)}
                    </p>
                    <p className="text-sm text-gray-500">
                      ${item.price.toFixed(2)} each
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Shipping Information */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-4">
              <MapPin className="h-5 w-5 text-gray-400 mr-2" />
              <h3 className="font-semibold text-gray-900">Shipping Address</h3>
            </div>
            <div className="text-gray-600">
              {typeof order.shipping_address === 'string' ? (
                <p>{order.shipping_address}</p>
              ) : (
                <pre className="whitespace-pre-wrap text-sm">
                  {JSON.stringify(order.shipping_address, null, 2)}
                </pre>
              )}
            </div>
          </div>

          {/* Billing Information */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-4">
              <CreditCard className="h-5 w-5 text-gray-400 mr-2" />
              <h3 className="font-semibold text-gray-900">Billing Address</h3>
            </div>
            <div className="text-gray-600">
              {typeof order.billing_address === 'string' ? (
                <p>{order.billing_address}</p>
              ) : (
                <pre className="whitespace-pre-wrap text-sm">
                  {JSON.stringify(order.billing_address, null, 2)}
                </pre>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 