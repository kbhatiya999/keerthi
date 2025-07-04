// User Types
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'customer' | 'admin' | 'super_admin';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
  name: string;
  role?: 'customer' | 'admin' | 'super_admin';
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
  role: string;
}

// Product Types
export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  category: string;
  stock_quantity: number;
  image_url?: string;
  sku?: string;
  brand?: string;
  tags: string[];
  rating?: number;
  review_count?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductCreate {
  name: string;
  description: string;
  price: number;
  category: string;
  stock_quantity: number;
  image_url?: string;
  sku?: string;
  brand?: string;
  tags?: string[];
}

// Cart Types
export interface CartItem {
  product_id: string;
  quantity: number;
}

export interface Cart {
  id: string;
  customer_id: string;
  items: CartItem[];
  created_at: string;
  updated_at: string;
}

export interface CartSummary {
  quantity: number;
  total: number;
}

// Order Types
export interface OrderItem {
  product_id: string;
  quantity: number;
  price: number;
  product_name?: string;
}

export interface Order {
  id: string;
  customer_id: string;
  items: OrderItem[];
  total_amount: number;
  status: 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled';
  payment_status: 'pending' | 'completed' | 'failed' | 'refunded';
  shipping_address: Record<string, any>;
  billing_address: Record<string, any>;
  created_at: string;
  updated_at: string;
  channel: string;
}

// Event Types
export interface Event {
  event_type: string;
  customer_id?: string;
  product_id?: string;
  session_id: string;
  timestamp: string;
  properties: Record<string, any>;
}

// API Response Types
export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

// Admin Stats
export interface AdminStats {
  total_users: number;
  total_products: number;
  total_orders: number;
  total_revenue: number;
} 