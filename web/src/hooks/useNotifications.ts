import { useToast, UseToastOptions } from "@chakra-ui/react";

type ToastParams = {
  title: string;
  description?: string;
};

export const useNotifications = () => {
  const toast = useToast();

  const showError = ({ title, description }: ToastParams) => {
    toast({
      title,
      description,
      status: "error",
      duration: 5000,
      isClosable: true,
      position: "top",
    });
  };

  const showSuccess = ({ title, description }: ToastParams) => {
    toast({
      title,
      description,
      status: "success",
      duration: 3000,
      isClosable: true,
      position: "bottom-right",
    });
  };

  return { showError, showSuccess };
};
