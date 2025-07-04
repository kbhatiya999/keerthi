import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { Token, User, Product, Cart, Order, CartSummary, AdminStats } from '@/types';

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Load token from localStorage on client side
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token');
      if (this.token) {
        this.setAuthToken(this.token);
      }
    }

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.logout();
        }
        return Promise.reject(error);
      }
    );
  }

  setAuthToken(token: string) {
    this.token = token;
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  logout() {
    this.token = null;
    delete this.client.defaults.headers.common['Authorization'];
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  // Authentication
  async login(email: string, password: string): Promise<Token> {
    const response = await this.client.post<Token>('/auth/login', { email, password });
    this.setAuthToken(response.data.access_token);
    return response.data;
  }

  async register(userData: { email: string; password: string; name: string; role?: string }): Promise<Token> {
    const response = await this.client.post<Token>('/auth/register', userData);
    this.setAuthToken(response.data.access_token);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/auth/me');
    return response.data;
  }

  // Products
  async getProducts(category?: string, search?: string): Promise<Product[]> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (search) params.append('search', search);
    
    const response = await this.client.get<Product[]>(`/products?${params.toString()}`);
    return response.data;
  }

  async getProduct(id: string): Promise<Product> {
    const response = await this.client.get<Product>(`/products/${id}`);
    return response.data;
  }

  async createProduct(productData: any): Promise<any> {
    const response = await this.client.post('/products', productData);
    return response.data;
  }

  async updateProduct(id: string, productData: any): Promise<any> {
    const response = await this.client.put(`/products/${id}`, productData);
    return response.data;
  }

  async deleteProduct(id: string): Promise<any> {
    const response = await this.client.delete(`/products/${id}`);
    return response.data;
  }

  // Cart
  async getCart(): Promise<Cart> {
    const response = await this.client.get<Cart>('/cart');
    return response.data;
  }

  async addToCart(productId: string, quantity: number): Promise<any> {
    const response = await this.client.post('/cart/items', { product_id: productId, quantity });
    return response.data;
  }

  async updateCartItemQuantity(productId: string, quantity: number): Promise<any> {
    const response = await this.client.put(`/cart/items/${productId}?quantity=${quantity}`);
    return response.data;
  }

  async removeFromCart(productId: string): Promise<any> {
    const response = await this.client.delete(`/cart/items/${productId}`);
    return response.data;
  }

  async clearCart(): Promise<any> {
    const response = await this.client.delete('/cart');
    return response.data;
  }

  async getCartSummary(): Promise<CartSummary> {
    const response = await this.client.get<CartSummary>('/cart/summary');
    return response.data;
  }

  async checkoutCart(checkoutData: any): Promise<any> {
    const response = await this.client.post('/cart/checkout', checkoutData);
    return response.data;
  }

  // Orders
  async getOrders(): Promise<Order[]> {
    const response = await this.client.get<Order[]>('/orders');
    return response.data;
  }

  async getOrder(id: string): Promise<Order> {
    const response = await this.client.get<Order>(`/orders/${id}`);
    return response.data;
  }

  async createOrder(orderData: any): Promise<any> {
    const response = await this.client.post('/orders', orderData);
    return response.data;
  }

  async updateOrder(id: string, orderData: any): Promise<any> {
    const response = await this.client.put(`/orders/${id}`, orderData);
    return response.data;
  }

  async deleteOrder(id: string): Promise<any> {
    const response = await this.client.delete(`/orders/${id}`);
    return response.data;
  }

  // Admin
  async getAdminStats(): Promise<AdminStats> {
    const response = await this.client.get<AdminStats>('/admin/stats');
    return response.data;
  }

  async getRecentOrders(limit: number = 10): Promise<Order[]> {
    const response = await this.client.get<Order[]>(`/admin/recent-orders?limit=${limit}`);
    return response.data;
  }

  async getUsers(): Promise<User[]> {
    const response = await this.client.get<User[]>('/users');
    return response.data;
  }

  // Events
  async trackEvent(eventData: any): Promise<any> {
    const response = await this.client.post('/events', eventData);
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<any> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

// Create singleton instance
export const api = new ApiClient();

// Legacy function for backward compatibility
export async function apiCall<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${path}`, {
    credentials: "include",
    ...init,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<T>;
}
