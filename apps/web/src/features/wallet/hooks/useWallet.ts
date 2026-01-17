/**
 * Wallet Feature - Hooks
 * خطافات ميزة المحفظة
 */

"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { walletApi } from "../api";
import type {
  TransactionFilters,
  TransferFormData,
  DepositFormData,
  WithdrawalFormData,
} from "../types";

// Query Keys
export const walletKeys = {
  all: ["wallet"] as const,
  wallet: () => [...walletKeys.all, "details"] as const,
  stats: () => [...walletKeys.all, "stats"] as const,
  transactions: {
    all: ["transactions"] as const,
    lists: () => [...walletKeys.transactions.all, "list"] as const,
    list: (filters?: TransactionFilters) =>
      [...walletKeys.transactions.lists(), filters] as const,
    detail: (id: string) =>
      [...walletKeys.transactions.all, "detail", id] as const,
  },
};

/**
 * Hook to fetch wallet details
 */
export function useWallet() {
  return useQuery({
    queryKey: walletKeys.wallet(),
    queryFn: () => walletApi.getWallet(),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

/**
 * Hook to fetch wallet statistics
 */
export function useWalletStats() {
  return useQuery({
    queryKey: walletKeys.stats(),
    queryFn: () => walletApi.getStats(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch transactions list
 */
export function useTransactions(filters?: TransactionFilters) {
  return useQuery({
    queryKey: walletKeys.transactions.list(filters),
    queryFn: () => walletApi.getTransactions(filters),
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

/**
 * Hook to fetch single transaction
 */
export function useTransaction(id: string) {
  return useQuery({
    queryKey: walletKeys.transactions.detail(id),
    queryFn: () => walletApi.getTransactionById(id),
    enabled: !!id,
  });
}

/**
 * Hook to create deposit
 */
export function useDeposit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: DepositFormData) => walletApi.deposit(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: walletKeys.wallet() });
      queryClient.invalidateQueries({ queryKey: walletKeys.stats() });
      queryClient.invalidateQueries({
        queryKey: walletKeys.transactions.lists(),
      });
    },
  });
}

/**
 * Hook to create withdrawal
 */
export function useWithdraw() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: WithdrawalFormData) => walletApi.withdraw(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: walletKeys.wallet() });
      queryClient.invalidateQueries({ queryKey: walletKeys.stats() });
      queryClient.invalidateQueries({
        queryKey: walletKeys.transactions.lists(),
      });
    },
  });
}

/**
 * Hook to transfer money
 */
export function useTransfer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TransferFormData) => walletApi.transfer(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: walletKeys.wallet() });
      queryClient.invalidateQueries({ queryKey: walletKeys.stats() });
      queryClient.invalidateQueries({
        queryKey: walletKeys.transactions.lists(),
      });
    },
  });
}
