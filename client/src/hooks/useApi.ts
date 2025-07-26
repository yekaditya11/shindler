// React Query Hooks for API calls

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  authApi,
  aiInsightsApi,
  dashboardApi,
  dataHealthApi,
  fileWorkflowApi,
  healthApi,
  chatApi,
} from '@/services/api';
import {
  LoginRequest,
  SchemaType,
  InsightFeedback,
} from '@/types/api';
import { httpClient } from '@/lib/http-client';

// Query Keys
export const queryKeys = {
  health: ['health'],
  dashboard: (schemaType: SchemaType, startDate?: string, endDate?: string) => 
    ['dashboard', schemaType, startDate, endDate],
  insights: (schemaType: SchemaType) => ['insights', schemaType],
  unifiedInsights: ['insights', 'unified'],
  dataHealth: (schemaType: SchemaType) => ['dataHealth', schemaType],
  dataHealthStatus: ['dataHealth', 'status'],
};

// Health Check Hook
export const useHealthCheck = () => {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: healthApi.checkHealth,
    retry: 3,
    retryDelay: 1000,
  });
};

// Authentication Hooks
export const useLogin = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (credentials: LoginRequest) => authApi.login(credentials),
    onSuccess: (data) => {
      httpClient.setToken(data.access_token);
      // Invalidate all queries that require authentication
      queryClient.invalidateQueries();
    },
    onError: (error) => {
      console.error('Login failed:', error);
    },
  });
};

export const useLogout = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      authApi.logout();
      return Promise.resolve();
    },
    onSuccess: () => {
      // Clear all cached data
      queryClient.clear();
    },
  });
};

// File Upload and Processing Hook
export const useFileUpload = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (file: File) => fileWorkflowApi.uploadAndProcess(file),
    onSuccess: () => {
      // Invalidate dashboard and insights queries after successful upload
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['insights'] });
      queryClient.invalidateQueries({ queryKey: ['dataHealth'] });
    },
  });
};

// Dashboard Hooks
export const useDashboardData = (
  schemaType: SchemaType,
  startDate?: string,
  endDate?: string,
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: queryKeys.dashboard(schemaType, startDate, endDate),
    queryFn: () => dashboardApi.getDashboardData(schemaType, startDate, endDate),
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// AI Insights Hooks
// Query existing insights for a schema
export const useInsights = (schemaType: SchemaType, enabled: boolean = true) => {
  return useQuery({
    queryKey: queryKeys.insights(schemaType),
    queryFn: () => aiInsightsApi.generateInsights(schemaType),
    enabled,
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: false, // Don't retry automatically
  });
};

export const useGenerateInsights = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (schemaType: SchemaType) => aiInsightsApi.generateInsights(schemaType),
    onSuccess: (data, schemaType) => {
      // Cache the generated insights
      queryClient.setQueryData(queryKeys.insights(schemaType), data);
    },
  });
};

export const useGenerateMoreInsights = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ schemaType, count }: { schemaType: SchemaType; count?: number }) =>
      aiInsightsApi.generateMoreInsights(schemaType, count),
    onSuccess: (data, { schemaType }) => {
      // Append new insights to existing ones
      queryClient.setQueryData(queryKeys.insights(schemaType), (oldData: any) => {
        if (!oldData) return data;
        return {
          ...data,
          body: {
            ...data.body,
            insights: [...(oldData.body?.insights || []), ...(data.body?.insights || [])]
          }
        };
      });
    },
  });
};

export const useGenerateUnifiedInsights = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: () => aiInsightsApi.generateUnifiedInsights(),
    onSuccess: (data) => {
      // Cache the generated unified insights
      queryClient.setQueryData(queryKeys.unifiedInsights, data);
    },
  });
};

export const useInsightFeedback = () => {
  return useMutation({
    mutationFn: (feedback: InsightFeedback) => aiInsightsApi.submitFeedback(feedback),
  });
};

// Data Health Hooks
export const useDataHealthStatus = () => {
  return useQuery({
    queryKey: queryKeys.dataHealthStatus,
    queryFn: dataHealthApi.getHealthStatus,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

export const useDataHealthReport = (schemaType: SchemaType, enabled: boolean = true) => {
  return useQuery({
    queryKey: queryKeys.dataHealth(schemaType),
    queryFn: () => dataHealthApi.getHealthReport(schemaType),
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Custom hook for checking authentication status
export const useAuthStatus = () => {
  return useQuery({
    queryKey: ['auth', 'status'],
    queryFn: authApi.validateToken,
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Chat Hooks
export const useSendChatMessage = () => {
  return useMutation({
    mutationFn: (message: string) => chatApi.sendMessage(message),
    onError: (error) => {
      console.error('Chat message failed:', error);
    },
  });
};
