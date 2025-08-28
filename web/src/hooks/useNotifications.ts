import { useToast } from "@chakra-ui/react";
import { useCallback } from "react";

type ToastParams = {
  title: string;
  description?: string;
};

export const useNotifications = () => {
  const toast = useToast();

  const showError = useCallback(
    ({ title, description }: ToastParams) => {
      toast({
        title,
        description,
        status: "error",
        duration: 5000,
        isClosable: true,
        position: "top",
      });
    },
    [toast]
  );

  const showSuccess = useCallback(
    ({ title, description }: ToastParams) => {
      toast({
        title,
        description,
        status: "success",
        duration: 3000,
        isClosable: true,
        position: "bottom-right",
      });
    },
    [toast]
  );

  return { showError, showSuccess };
};
