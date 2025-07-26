import { useState, useRef, useEffect } from "react";
import { X, Send, MessageCircle, Minimize2, Maximize2, Bot, User, Volume2, RotateCcw, Mic, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { ChatBotChart } from "./ChatBotChart";

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  isTyping?: boolean;
  displayContent?: string;
  visualizationData?: Record<string, unknown>;
}

interface ChatBotProps {
  isOpen: boolean;
  onToggle: () => void;
  onSendMessage?: (message: string) => Promise<{ text: string; visualizationData?: Record<string, unknown> }>;
  onSaveToDashboard?: (chartData: Record<string, unknown>, title: string, description: string) => Promise<void>;
}

export const ChatBotFloatingIcon = ({ onToggle, isOpen }: { onToggle: () => void; isOpen: boolean }) => {
  return (
    <div className="fixed bottom-6 right-6 z-50">
      <Button
        onClick={onToggle}
        className={cn(
          "w-16 h-16 rounded-full relative overflow-hidden transition-all duration-300 transform hover:scale-105 border-0 p-0",
          "bg-[#1e3a8a] hover:bg-[#1e40af]",
          "shadow-[0_4px_20px_rgba(30,58,138,0.3)] hover:shadow-[0_6px_25px_rgba(30,58,138,0.4)]",
          isOpen && "bg-[#dc2626] hover:bg-[#b91c1c]"
        )}
      >
        {/* Icon */}
        <div className="relative z-10 flex items-center justify-center h-full">
          {isOpen ? (
            <X className="h-7 w-7 text-white" />
          ) : (
            <Bot className="h-8 w-8 text-white" />
          )}
        </div>
      </Button>
    </div>
  );
};

// Function to format bot responses with better styling
const formatBotResponse = (content: string): string => {
  // Replace plain numbers with formatted numbers
  const formatted = content
    // Format numbers with commas (e.g., 877 -> 877)
    .replace(/(\d+)/g, (match) => {
      const num = parseInt(match);
      return num.toLocaleString();
    })
    // Format percentages
    .replace(/(\d+)%/g, '$1%')
    // Add line breaks for better readability
    .replace(/\. /g, '.\n\n')
    .replace(/! /g, '!\n\n')
    .replace(/\? /g, '?\n\n');

  return formatted;
};

export const ChatBot = ({ isOpen, onToggle, onSendMessage, onSaveToDashboard }: ChatBotProps) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hi! I\'m Safety Assistant. How can I help you?',
      sender: 'bot',
      timestamp: new Date(),
      displayContent: 'Hi! I\'m Safety Assistant. How can I help you?'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Typing animation effect
  useEffect(() => {
    const typingMessages = messages.filter(msg => msg.isTyping);
    
    typingMessages.forEach(message => {
      const fullContent = message.content;
      let currentIndex = 0;
      
      const typingInterval = setInterval(() => {
        currentIndex++;
        const displayContent = fullContent.slice(0, currentIndex);
        
        setMessages(prev => prev.map(msg => 
          msg.id === message.id 
            ? { ...msg, displayContent }
            : msg
        ));
        
        if (currentIndex >= fullContent.length) {
          clearInterval(typingInterval);
          setMessages(prev => prev.map(msg => 
            msg.id === message.id 
              ? { ...msg, isTyping: false, displayContent: fullContent }
              : msg
          ));
        }
      }, 30); // Adjust speed here (lower = faster)
      
      return () => clearInterval(typingInterval);
    });
  }, [messages.filter(msg => msg.isTyping).length]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage.trim(),
      sender: 'user',
      timestamp: new Date(),
      displayContent: inputMessage.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      let botResponse = { text: 'Thank you for your message. I\'m here to help with driver safety questions.' };
      let visualizationData = null;
      
      if (onSendMessage) {
        const response = await onSendMessage(userMessage.content);
        botResponse = response;
        visualizationData = response.visualizationData;
      }

      // Format the bot response
      const formattedResponse = formatBotResponse(botResponse.text);

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: formattedResponse,
        sender: 'bot',
        timestamp: new Date(),
        isTyping: true,
        displayContent: '',
        visualizationData: visualizationData
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
        displayContent: 'Sorry, I encountered an error. Please try again.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <div className={cn(
      "fixed z-[60] transition-all duration-300",
      isExpanded 
        ? "inset-0 flex items-center justify-center p-4" 
        : "bottom-24 right-6"
    )}>
      {isExpanded && (
        <div className="absolute inset-0 bg-black/20" onClick={() => setIsExpanded(false)} />
      )}
      <div className={cn(
        "bg-white rounded-t-xl rounded-b-2xl shadow-2xl transition-all duration-300 flex flex-col border-0 overflow-hidden",
        isExpanded
          ? "w-[600px] h-[700px] max-w-[90vw] max-h-[90vh]"
          : "w-[450px] h-[600px]"
      )}>
        {/* Header - Dark Blue */}
        <div className="flex items-center justify-between px-4 py-3 bg-[#1e3a8a] text-white">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
              <Bot className="h-5 w-5 text-white" />
            </div>
            <h3 className="font-medium text-sm">Safety Assistant</h3>
          </div>
          
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              className="h-7 w-7 p-0 text-white hover:bg-white/10 rounded-md"
              title="Sound"
            >
              <Volume2 className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="h-7 w-7 p-0 text-white hover:bg-white/10 rounded-md"
              title={isExpanded ? "Minimize" : "Expand"}
            >
              {isExpanded ? <Minimize2 className="h-3.5 w-3.5" /> : <Maximize2 className="h-3.5 w-3.5" />}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-7 w-7 p-0 text-white hover:bg-white/10 rounded-md"
              title="Refresh"
            >
              <RotateCcw className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>

        {/* Messages Area - Clean White */}
        <ScrollArea className="flex-1 p-4 bg-white">
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex gap-3",
                  message.sender === 'user' ? "justify-end" : "justify-start"
                )}
              >
                {message.sender === 'bot' && (
                  <div className="w-7 h-7 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0 mt-1">
                    <Bot className="h-4 w-4 text-gray-600" />
                  </div>
                )}
                
                <div className={cn(
                  "max-w-[75%] flex flex-col",
                  message.sender === 'user' ? "items-end" : "items-start"
                )}>
                  <div
                    className={cn(
                      "rounded-2xl px-4 py-2.5 text-sm",
                      message.sender === 'user'
                        ? "bg-[#1e3a8a] text-white"
                        : "bg-gray-100 text-gray-800"
                    )}
                  >
                    <div className="whitespace-pre-line">
                      {message.displayContent || message.content}
                      {message.isTyping && (
                        <span className="inline-block w-2 h-4 bg-gray-600 ml-1 animate-pulse"></span>
                      )}
                    </div>
                  </div>
                  
                  {/* Chart Visualization */}
                  {message.sender === 'bot' && message.visualizationData && !message.isTyping && (
                    <div className="mt-3 w-full">
                      <ChatBotChart 
                        chartData={message.visualizationData} 
                        className="w-full"
                        width="100%"
                        height={250}
                        showSaveButton={true}
                        onSaveToDashboard={onSaveToDashboard}
                      />
                    </div>
                  )}
                  
                  <p className="text-xs text-gray-400 mt-1 px-1">
                    {message.timestamp.toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                      hour12: true
                    })}
                  </p>
                </div>

                {message.sender === 'user' && (
                  <div className="w-7 h-7 rounded-full bg-[#1e3a8a] flex items-center justify-center flex-shrink-0 mt-1">
                    <User className="h-4 w-4 text-white" />
                  </div>
                )}
              </div>
            ))}
            
            {isLoading && (
              <div className="flex gap-3 justify-start">
                <div className="w-7 h-7 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0 mt-1">
                  <Bot className="h-4 w-4 text-gray-600" />
                </div>
                <div className="bg-gray-100 rounded-2xl px-4 py-2.5">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Input Area - Clean White */}
        <div className="p-4 bg-white border-t border-gray-100">
          <div className="flex gap-2 items-center">
            <div className="flex-1 relative">
              <Input
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your message..."
                disabled={isLoading}
                className="pr-10 border-gray-200 focus:border-[#1e3a8a] focus:ring-[#1e3a8a] rounded-xl bg-gray-50"
              />
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 p-0 text-gray-400 hover:text-gray-600 rounded-lg"
                title="Voice message"
              >
                <Mic className="h-4 w-4" />
              </Button>
            </div>
            <Button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="bg-[#1e3a8a] hover:bg-[#1e40af] h-10 w-10 p-0 rounded-xl"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
