// web/src/components/ChatBotInterface.tsx
import React, { useState, useRef, useEffect } from "react";
import {
  Box,
  VStack,
  HStack,
  Text,
  Input,
  IconButton,
  Avatar,
  Spinner,
  useColorModeValue,
  Flex,
  useToast,
} from "@chakra-ui/react";
import { ArrowUpIcon, CloseIcon } from "@chakra-ui/icons";
import { sendChatMessage } from "../api/chatbot";

interface ChatMessage {
  id: string;
  type: "user" | "assistant";
  content: string;
  timestamp: Date;
  isTyping?: boolean;
}

interface ChatbotInterfaceProps {
  groupId: string;
  isOpen: boolean;
  onClose: () => void;
  onExpenseAdded?: () => void;
}

const ChatbotInterface: React.FC<ChatbotInterfaceProps> = ({
  groupId,
  isOpen,
  onClose,
  onExpenseAdded,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      type: "assistant",
      content:
        "Hi! I'm your expense assistant. I can help you add expenses, check balances, and answer questions about your group's finances. What would you like to do?",
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const toast = useToast();

  const bgColor = useColorModeValue("white", "gray.800");
  const borderColor = useColorModeValue("gray.200", "gray.600");
  const userBg = useColorModeValue("blue.500", "blue.600");
  const assistantBg = useColorModeValue("gray.100", "gray.700");
  const headerBg = useColorModeValue("blue.500", "blue.600");

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: "user",
      content: inputMessage.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = inputMessage.trim();
    setInputMessage("");
    setIsLoading(true);

    // Add typing indicator
    const typingMessage: ChatMessage = {
      id: "typing",
      type: "assistant",
      content: "",
      timestamp: new Date(),
      isTyping: true,
    };
    setMessages((prev) => [...prev, typingMessage]);

    try {
      const response = await sendChatMessage(currentInput, groupId);

      // Remove typing indicator
      setMessages((prev) => prev.filter((msg) => msg.id !== "typing"));

      const assistantMessage: ChatMessage = {
        id: Date.now().toString(),
        type: "assistant",
        content: response.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Check if an expense was added
      if (
        response.response.toLowerCase().includes("added expense") ||
        response.response.toLowerCase().includes("expense of") ||
        response.response.toLowerCase().includes("successfully added")
      ) {
        onExpenseAdded?.();
        toast({
          title: "Expense Added",
          description: "A new expense has been added to your group!",
          status: "success",
          duration: 3000,
          isClosable: true,
        });
      }
    } catch (error) {
      console.error("Chat error:", error);

      // Remove typing indicator
      setMessages((prev) => prev.filter((msg) => msg.id !== "typing"));

      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        type: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);

      toast({
        title: "Error",
        description: "Failed to send message. Please try again.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  if (!isOpen) return null;

  return (
    <Box
      position="fixed"
      bottom="20px"
      right="20px"
      width="380px"
      height={isMinimized ? "60px" : "500px"}
      bg={bgColor}
      border="1px solid"
      borderColor={borderColor}
      borderRadius="12px"
      shadow="xl"
      display="flex"
      flexDirection="column"
      zIndex={1000}
      transition="height 0.3s ease"
    >
      {/* Header */}
      <Flex
        align="center"
        justify="space-between"
        p={3}
        bg={headerBg}
        color="white"
        borderRadius="12px 12px 0 0"
        cursor="pointer"
        onClick={() => setIsMinimized(!isMinimized)}
      >
        <HStack spacing={3}>
          <Avatar size="sm" bg="white" color={headerBg}>
            <Text fontWeight="bold" fontSize="sm">
              AI
            </Text>
          </Avatar>
          <VStack align="start" spacing={0}>
            <Text fontWeight="bold" fontSize="sm">
              Expense Assistant
            </Text>
            <Text fontSize="xs" opacity={0.9}>
              {isMinimized ? "Click to expand" : "AI-powered help"}
            </Text>
          </VStack>
        </HStack>
        <HStack spacing={1}>
          <IconButton
            aria-label="Minimize chat"
            // icon={<MinimizeIcon />}
            size="xs"
            variant="ghost"
            color="white"
            onClick={(e) => {
              e.stopPropagation();
              setIsMinimized(!isMinimized);
            }}
          />
          <IconButton
            aria-label="Close chat"
            icon={<CloseIcon />}
            size="xs"
            variant="ghost"
            color="white"
            onClick={(e) => {
              e.stopPropagation();
              onClose();
            }}
          />
        </HStack>
      </Flex>

      {!isMinimized && (
        <>
          {/* Messages */}
          <VStack
            flex={1}
            p={3}
            spacing={3}
            overflowY="auto"
            align="stretch"
            maxH="350px"
          >
            {messages.map((message) => (
              <Box key={message.id}>
                {message.isTyping ? (
                  <HStack spacing={2} align="center">
                    <Avatar size="xs" bg="gray.400">
                      <Text fontSize="xs" color="white" fontWeight="bold">
                        AI
                      </Text>
                    </Avatar>
                    <Box bg={assistantBg} p={2} borderRadius="lg" maxW="80%">
                      <HStack spacing={2}>
                        <Spinner size="xs" color="blue.500" />
                        <Text fontSize="xs" color="gray.500">
                          Typing...
                        </Text>
                      </HStack>
                    </Box>
                  </HStack>
                ) : (
                  <HStack
                    spacing={2}
                    align="start"
                    justify={
                      message.type === "user" ? "flex-end" : "flex-start"
                    }
                  >
                    {message.type === "assistant" && (
                      <Avatar size="xs" bg="blue.500">
                        <Text fontSize="xs" color="white" fontWeight="bold">
                          AI
                        </Text>
                      </Avatar>
                    )}
                    <VStack
                      align={message.type === "user" ? "end" : "start"}
                      spacing={1}
                      maxW="80%"
                    >
                      <Box
                        bg={message.type === "user" ? userBg : assistantBg}
                        color={message.type === "user" ? "white" : "inherit"}
                        p={2}
                        borderRadius="lg"
                        border={
                          message.type === "assistant" ? "1px solid" : "none"
                        }
                        borderColor={
                          message.type === "assistant"
                            ? borderColor
                            : "transparent"
                        }
                      >
                        <Text fontSize="sm" whiteSpace="pre-wrap">
                          {message.content}
                        </Text>
                      </Box>
                      <Text fontSize="xs" color="gray.500">
                        {formatTime(message.timestamp)}
                      </Text>
                    </VStack>
                    {message.type === "user" && (
                      <Avatar size="xs" bg="green.500">
                        <Text fontSize="xs" color="white" fontWeight="bold">
                          U
                        </Text>
                      </Avatar>
                    )}
                  </HStack>
                )}
              </Box>
            ))}
            <div ref={messagesEndRef} />
          </VStack>

          {/* Input */}
          <Box p={3} borderTop="1px solid" borderColor={borderColor}>
            <HStack spacing={2}>
              <Input
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                size="sm"
                disabled={isLoading}
                borderRadius="full"
              />
              <IconButton
                aria-label="Send message"
                icon={<ArrowUpIcon />}
                size="sm"
                colorScheme="blue"
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
                isLoading={isLoading}
                borderRadius="full"
                minW="36px"
                h="36px"
              />
            </HStack>
            <Text fontSize="xs" color="gray.500" mt={1} textAlign="center">
              Try: "Add €25 dinner paid by John"
            </Text>
          </Box>
        </>
      )}
    </Box>
  );
};

export default ChatbotInterface;
