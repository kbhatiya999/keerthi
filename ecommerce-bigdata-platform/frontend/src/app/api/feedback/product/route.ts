import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const token = request.headers.get('authorization')?.replace('Bearer ', '');

    if (!token || token === 'null') {
      return NextResponse.json(
        { detail: 'Authentication required' },
        { status: 401 }
      );
    }

    // Validate required fields
    if (!body.product_id || !body.rating || !body.text) {
      return NextResponse.json(
        { detail: 'Missing required fields: product_id, rating, text' },
        { status: 400 }
      );
    }

    // Transform the payload to match backend expectations
    const backendPayload = {
      product_id: body.product_id,
      rating: body.rating,
      comment: body.text,
      sentiment: 'positive' // Default sentiment, will be updated by Databricks
    };

    // Forward the request to the backend
    const response = await fetch('http://localhost:8000/feedback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(backendPayload)
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Product feedback submission error:', error);
    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
} 