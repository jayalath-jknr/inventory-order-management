// API Types
export interface Product {
  id: number;
  name: string;
  price: string;
  stock_quantity: number;
}

export interface ProductCreate {
  name: string;
  price: string;
  stock_quantity: number;
}

export interface ProductListResponse {
  items: Product[];
  total: number;
  skip: number;
  limit: number;
}

export type OrderStatus = 'pending' | 'shipped' | 'cancelled';

export interface OrderItem {
  id: number;
  product_id: number;
  quantity: number;
  price_at_order: string;
}

export interface Order {
  id: number;
  created_at: string;
  status: OrderStatus;
  items: OrderItem[];
}

export interface OrderCreate {
  items: { product_id: number; quantity: number }[];
}

export interface OrderStatusUpdate {
  status: OrderStatus;
}

// API Client
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Products
  async getProducts(skip = 0, limit = 20): Promise<ProductListResponse> {
    return this.request(`/products?skip=${skip}&limit=${limit}`);
  }

  async createProduct(product: ProductCreate): Promise<Product> {
    return this.request('/products', {
      method: 'POST',
      body: JSON.stringify(product),
    });
  }

  // Orders
  async getOrders(): Promise<Order[]> {
    // Fetch multiple orders - we'll get them one by one for now
    // In a real app, you'd have a list endpoint
    const orders: Order[] = [];
    for (let i = 1; i <= 50; i++) {
      try {
        const order = await this.getOrder(i);
        orders.push(order);
      } catch {
        // Order doesn't exist, stop
        break;
      }
    }
    return orders;
  }

  async getOrder(orderId: number): Promise<Order> {
    return this.request(`/orders/${orderId}`);
  }

  async createOrder(order: OrderCreate): Promise<Order> {
    return this.request('/orders', {
      method: 'POST',
      body: JSON.stringify(order),
    });
  }

  async updateOrderStatus(orderId: number, status: OrderStatus): Promise<Order> {
    return this.request(`/orders/${orderId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  }
}

export const api = new ApiClient();
