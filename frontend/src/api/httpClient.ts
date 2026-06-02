const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5000';

function getHeaders(): HeadersInit {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  const token = localStorage.getItem('access_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
}

export async function apiGet<TResponse>(path: string): Promise<TResponse> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    method: 'GET',
    headers: getHeaders(),
  });

  if (!response.ok) {
    let errorMessage = `Request failed with status ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson && typeof errJson === 'object' && 'message' in errJson) {
        errorMessage = errJson.message as string;
      } else if (errJson && typeof errJson === 'string') {
        errorMessage = errJson;
      }
    } catch {
      // Ignored
    }
    throw new Error(errorMessage);
  }

  return response.json() as Promise<TResponse>;
}

export async function apiPost<TBody, TResponse>(path: string, body: TBody): Promise<TResponse> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    let errorMessage = `Request failed with status ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson && typeof errJson === 'object') {
        if ('message' in errJson) {
          errorMessage = errJson.message as string;
        } else if ('error' in errJson && typeof errJson.error === 'string') {
          errorMessage = errJson.error;
        } else if ('error' in errJson && typeof errJson.error === 'object' && errJson.error && 'message' in errJson.error) {
          errorMessage = (errJson.error as { message: string }).message;
        }
      } else if (errJson && typeof errJson === 'string') {
        errorMessage = errJson;
      }
    } catch {
      // Ignored
    }
    throw new Error(errorMessage);
  }

  return response.json() as Promise<TResponse>;
}
