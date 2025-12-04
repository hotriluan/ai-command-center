'use client';

import { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Bot, User } from 'lucide-react';

export default function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<{ role: 'user' | 'ai'; content: string }[]>([
        { role: 'ai', content: 'Hello! I am your AI Business Analyst. How can I help you today?' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isOpen]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage = input;
        setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
        setInput('');
        setIsLoading(true);

        try {
            const res = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: userMessage }),
            });
            const data = await res.json();
            setMessages((prev) => [...prev, { role: 'ai', content: data.answer }]);
        } catch (error) {
            setMessages((prev) => [...prev, { role: 'ai', content: 'Sorry, I am having trouble connecting to the server.' }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="fixed bottom-6 right-6 z-[100] flex flex-col items-end font-sans">
            {/* Chat Window */}
            {isOpen && (
                <div className="mb-4 w-[380px] h-[600px] max-h-[80vh] bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col overflow-hidden animate-in slide-in-from-bottom-10 fade-in duration-500">
                    {/* Header */}
                    <div className="bg-slate-900 p-4 flex justify-between items-center text-white shadow-md">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-white/10 rounded-lg backdrop-blur-sm">
                                <Bot size={20} className="text-white" />
                            </div>
                            <div>
                                <h3 className="font-semibold text-base tracking-wide">AI Command Center</h3>
                                <p className="text-xs text-slate-300 flex items-center gap-1.5">
                                    <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]"></span>
                                    Online
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={() => setIsOpen(false)}
                            className="hover:bg-white/10 p-2 rounded-lg transition-all duration-200 hover:scale-105 active:scale-95"
                            aria-label="Close chat"
                        >
                            <X size={20} />
                        </button>
                    </div>

                    {/* Messages Area */}
                    <div className="flex-1 overflow-y-auto p-5 bg-slate-50 space-y-4">
                        {messages.map((msg, index) => (
                            <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
                                <div className={`flex gap-3 max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                                    {/* Avatar */}
                                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm ${msg.role === 'user' ? 'bg-blue-700 text-white' : 'bg-white border border-slate-200 text-slate-700'
                                        }`}>
                                        {msg.role === 'user' ? <User size={14} /> : <Bot size={16} />}
                                    </div>

                                    {/* Message Bubble */}
                                    <div className={`px-4 py-3 text-sm leading-relaxed shadow-sm ${msg.role === 'user'
                                            ? 'bg-blue-700 text-white rounded-2xl rounded-tr-sm'
                                            : 'bg-white text-slate-800 border border-slate-200 rounded-2xl rounded-tl-sm'
                                        }`}>
                                        {msg.content}
                                    </div>
                                </div>
                            </div>
                        ))}

                        {isLoading && (
                            <div className="flex justify-start animate-in fade-in duration-300">
                                <div className="flex gap-3 max-w-[85%]">
                                    <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm bg-white border border-slate-200 text-slate-700">
                                        <Bot size={16} />
                                    </div>
                                    <div className="bg-white border border-slate-200 px-5 py-4 rounded-2xl rounded-tl-sm shadow-sm">
                                        <div className="flex space-x-1.5">
                                            <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></div>
                                            <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                            <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    <div className="p-4 bg-white border-t border-slate-100 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
                        <div className="relative flex items-center">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && !isLoading && handleSend()}
                                placeholder="Type your message..."
                                className="w-full bg-slate-50 text-slate-800 text-sm rounded-full pl-5 pr-12 py-3.5 focus:outline-none focus:ring-2 focus:ring-slate-900/10 focus:bg-white transition-all duration-200 border border-slate-200 placeholder:text-slate-400"
                                disabled={isLoading}
                            />
                            <button
                                onClick={handleSend}
                                disabled={isLoading || !input.trim()}
                                className="absolute right-2 p-2 bg-slate-900 hover:bg-slate-800 text-white rounded-full transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm hover:shadow-md active:scale-95"
                                aria-label="Send message"
                            >
                                <Send size={16} />
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Floating Toggle Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="group relative flex items-center justify-center w-16 h-16 bg-slate-900 text-white rounded-full shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-300 active:scale-95"
                aria-label={isOpen ? "Close chat" : "Open chat"}
            >
                <div className={`transition-all duration-300 ${isOpen ? 'rotate-90 scale-100' : 'rotate-0 scale-100'}`}>
                    {isOpen ? (
                        <X size={28} className="animate-in spin-in-90 duration-200" />
                    ) : (
                        <MessageSquare size={28} className="animate-in zoom-in duration-200" />
                    )}
                </div>
            </button>
        </div>
    );
}
