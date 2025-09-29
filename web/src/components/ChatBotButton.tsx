// web/src/components/ChatbotButton.tsx
import React from "react";
import { IconButton, useColorModeValue, Tooltip, Box } from "@chakra-ui/react";

interface ChatbotButtonProps {
  onClick: () => void;
}

const ChatbotButton: React.FC<ChatbotButtonProps> = ({ onClick }) => {
  const bgColor = useColorModeValue("#10a37f", "#10a37f");
  const hoverBg = useColorModeValue("#0d8f6b", "#0d8f6b");

  return (
    <Box position="fixed" bottom="24px" right="24px" zIndex={999}>
      <Tooltip label="Chat with AI Assistant" placement="left" hasArrow>
        <IconButton
          aria-label="Open chat"
          //   icon={<MessageIcon />}
          size="lg"
          bg={bgColor}
          color="white"
          _hover={{
            bg: hoverBg,
            transform: "scale(1.05)",
            transition: "all 0.2s",
          }}
          _active={{
            transform: "scale(0.95)",
          }}
          borderRadius="full"
          shadow="lg"
          width="56px"
          height="56px"
          onClick={onClick}
        />
      </Tooltip>
    </Box>
  );
};

export default ChatbotButton;
