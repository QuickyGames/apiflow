import { PUBLIC_API_URL } from '$env/static/public';

export interface Connector {
  id: number;
  name: string;
  base_url: string;
  method: string;
  header: Record<string, any>;
  body: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Node {
  id: number;
  name: string;
  description: string;
  connector_id: number;
  path: string;
  input: any[];
  output: any[];
  data: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Workflow {
  id: number;
  name: string;
  description: string;
  nodes: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: number;
  name: string;
  workflow_id: number;
  workflow_name: string;
  status: string;
  retry_count: number;
  input: Record<string, any>;
  output: Record<string, any>;
  error: string | null;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  api_token: string;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor() {
    this.baseUrl = PUBLIC_API_URL || 'http://localhost:8000';
    // Get token from localStorage
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('api_token');
    }
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('api_token', token);
    }
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('api_token');
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers: {
        ...headers,
        ...(options.headers as Record<string, string>),
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // Connector methods
  async getConnectors(): Promise<Connector[]> {
    return this.request('/api/v1/connectors');
  }

  async getConnector(id: number): Promise<Connector> {
    return this.request(`/api/v1/connectors/${id}`);
  }

  async createConnector(data: Omit<Connector, 'id' | 'created_at' | 'updated_at'>): Promise<Connector> {
    return this.request('/api/v1/connectors', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateConnector(id: number, data: Partial<Connector>): Promise<Connector> {
    return this.request(`/api/v1/connectors/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteConnector(id: number): Promise<void> {
    return this.request(`/api/v1/connectors/${id}`, {
      method: 'DELETE',
    });
  }

  // Node methods
  async getNodes(): Promise<Node[]> {
    return this.request('/api/v1/nodes');
  }

  async getNode(id: number): Promise<Node> {
    return this.request(`/api/v1/nodes/${id}`);
  }

  async createNode(data: Omit<Node, 'id' | 'created_at' | 'updated_at'>): Promise<Node> {
    return this.request('/api/v1/nodes', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateNode(id: number, data: Partial<Node>): Promise<Node> {
    return this.request(`/api/v1/nodes/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteNode(id: number): Promise<void> {
    return this.request(`/api/v1/nodes/${id}`, {
      method: 'DELETE',
    });
  }

  async runNode(id: number, input: Record<string, any>): Promise<any> {
    return this.request(`/api/v1/node/${id}/run`, {
      method: 'POST',
      body: JSON.stringify({ input }),
    });
  }

  // Workflow methods
  async getWorkflows(): Promise<Workflow[]> {
    return this.request('/api/v1/workflows');
  }

  async getWorkflow(id: number): Promise<Workflow> {
    return this.request(`/api/v1/workflows/${id}`);
  }

  async createWorkflow(data: Omit<Workflow, 'id' | 'created_at' | 'updated_at'>): Promise<Workflow> {
    return this.request('/api/v1/workflows', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateWorkflow(id: number, data: Partial<Workflow>): Promise<Workflow> {
    return this.request(`/api/v1/workflows/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteWorkflow(id: number): Promise<void> {
    return this.request(`/api/v1/workflows/${id}`, {
      method: 'DELETE',
    });
  }

  async runWorkflow(id: number, input: Record<string, any>): Promise<any> {
    return this.request(`/api/v1/workflow/${id}/run`, {
      method: 'POST',
      body: JSON.stringify({ input }),
    });
  }

  // Job methods
  async getJobs(): Promise<Job[]> {
    return this.request('/api/v1/jobs');
  }

  async getJob(id: number): Promise<Job> {
    return this.request(`/api/v1/jobs/${id}`);
  }

  async getWorkflowJobs(workflowId: number): Promise<Job[]> {
    return this.request(`/api/v1/workflow/${workflowId}/jobs`);
  }

  async cancelJob(id: number): Promise<any> {
    return this.request(`/api/v1/jobs/${id}/cancel`, {
      method: 'POST',
    });
  }

  // User methods
  async getUser(id: number): Promise<User> {
    return this.request(`/api/v1/user/${id}`);
  }

  async updateUser(data: { username?: string; email?: string }): Promise<User> {
    return this.request('/api/v1/user', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async resetUserToken(id: number): Promise<{ status: string; new_token: string }> {
    return this.request(`/api/v1/user/${id}/reset_token`, {
      method: 'POST',
    });
  }

  async deleteUser(): Promise<void> {
    return this.request('/api/v1/user', {
      method: 'DELETE',
    });
  }
}

export const api = new ApiClient();
