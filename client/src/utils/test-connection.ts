// Test Server Connection Utility

import { healthApi } from '@/services/api';

export const testServerConnection = async (): Promise<{
  success: boolean;
  message: string;
  serverInfo?: any;
}> => {
  try {
    console.log('Testing server connection...');
    
    const response = await healthApi.checkHealth();
    
    return {
      success: true,
      message: 'Server connection successful!',
      serverInfo: response,
    };
  } catch (error) {
    console.error('Server connection failed:', error);
    
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Unknown connection error',
    };
  }
};

// Test function to be called from browser console
(window as any).testConnection = testServerConnection;
