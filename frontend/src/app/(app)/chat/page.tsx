"use client"

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { SearchInput } from '@/components/ui/search-input'
import {
  Clock,
  History,
  MessageSquare,
  Plus,
  SendHorizonal,
  Trash2,
} from 'lucide-react'
import React, { useState } from 'react'

interface ChatHistoryItem {
  id: string
  title: string
  timestamp: string
  preview: string
}

const Chat = () => {
  const [open, setOpen] = useState(false)
  const [history, setHistory] = useState<ChatHistoryItem[]>([])
  const [activeChatId, setActiveChatId] = useState<string | null>(null)
  const [historySearch, setHistorySearch] = useState('')

  // TODO: IMPLEMENT THE CHAT API FROM THE HOOKS
  const handleNewChat = () => {
    const newChat: ChatHistoryItem = {
      id: Date.now().toString(),
      title: 'New Conversation',
      timestamp: 'Just now',
      preview: 'Start chatting...',
    }
    setHistory((prev) => [newChat, ...prev])
    setActiveChatId(newChat.id)
    setOpen(false)
  }

  const handleSelectChat = (id: string) => {
    setActiveChatId(id)
    setOpen(false)
  }

  // TODO : FILTER REAL HISTORY CHATS 
  const filteredHistory = history.filter(
    (item) =>
      item.title.toLowerCase().includes(historySearch.toLowerCase()) ||
      item.preview.toLowerCase().includes(historySearch.toLowerCase())
  )

  const activeChat = history.find((h) => h.id === activeChatId)

  return (
    <section className="relative flex flex-col h-[calc(100vh-6rem)] md:h-[calc(100vh-6.5rem)]">
      
      {/* FLOATING CHAT HISTORY DIALOG TRIGGER */}
      <div className="absolute top-0 right-0 z-20">
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger
            render={
              <Button
                variant="outline"
                size="sm"
                className="flex items-center gap-1.5 rounded-full bg-card/80 backdrop-blur-md shadow-md border-border/80 hover:bg-card text-foreground text-xs px-3 py-1.5 transition-all"
              />
            }
          >
            <History className="h-3.5 w-3.5 text-primary" />
            <span>Chat History</span>
          </DialogTrigger>

          <DialogContent className="sm:max-w-md p-5 gap-4">
            <DialogHeader className="gap-1.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <History className="h-5 w-5 text-primary" />
                  <DialogTitle className="text-lg">Chat History</DialogTitle>
                </div>
              </div>
            </DialogHeader>

            {/* SEARCH INPUT */}
            <SearchInput
              value={historySearch}
              onChange={(e) => setHistorySearch(e.target.value)}
              placeholder="Search history..."
              showClear
              onClear={() => setHistorySearch('')}
              className="h-9 text-sm"
            />

            {/* HISTORY LIST */}
            {/* TODO : LOAD REAL HISTORY CHATS HERE  */}
            <div className="max-h-72 overflow-y-auto space-y-2 pr-1 -mr-1">
              {filteredHistory.length === 0 ? (
                <div className="text-center py-8 text-sm text-muted-foreground">
                  No conversation history found
                </div>
              ) : (
                filteredHistory.map((item) => {
                  const isActive = item.id === activeChatId
                  return (
                    <div
                      key={item.id}
                      onClick={() => handleSelectChat(item.id)}
                      className={`group flex items-start justify-between gap-3 p-3 rounded-lg cursor-pointer transition-all border text-left ${
                        isActive
                          ? 'bg-primary/10 border-primary/40 text-foreground'
                          : 'bg-muted/30 border-transparent hover:bg-muted/70 text-muted-foreground hover:text-foreground'
                      }`}
                    >
                      <div className="flex items-start gap-2.5 min-w-0 flex-1">
                        <MessageSquare
                          className={`h-4 w-4 mt-0.5 shrink-0 ${
                            isActive ? 'text-primary' : 'text-muted-foreground'
                          }`}
                        />
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-medium truncate text-foreground">
                            {item.title}
                          </p>
                          <p className="text-xs text-muted-foreground truncate mt-0.5">
                            {item.preview}
                          </p>
                          <div className="flex items-center gap-1.5 mt-1.5 text-[11px] text-muted-foreground/80">
                            <Clock className="h-3 w-3" />
                            <span>{item.timestamp}</span>
                          </div>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon-xs"
                        onClick={() => {}}
                        className="opacity-0 group-hover:opacity-100 hover:text-destructive hover:bg-destructive/10 transition-all h-7 w-7 shrink-0"
                        title="Delete chat"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  )
                })
              )}
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* SCROLLABLE HISTORY CHAT CONTAINER */}
      <main className="flex-1 overflow-y-auto space-y-4 pt-10">
        <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground text-sm gap-2 max-w-md mx-auto">
          <MessageSquare className="h-8 w-8 text-muted-foreground/50 mb-1" />
          <p className="font-medium text-foreground text-base">
            {activeChat ? activeChat.title : 'New Conversation'}
          </p>
          <p className="text-xs text-muted-foreground">
            {activeChat
              ? `Viewing active session: "${activeChat.preview}"`
              : 'Ask a question below to start your conversation.'}
          </p>
        </div>
      </main>

      {/* INPUT BAR PINNED AT BOTTOM */}
      <footer className="pt-4 shrink-0">
        <form
          onSubmit={(e) => e.preventDefault()}
          className="flex items-center gap-2 w-full"
        >
          <div className="relative flex-1 bg-card">
            <SendHorizonal className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
            <Input
              type="search"
              placeholder="Ask anything..."
              className="pl-9 h-10 w-full"
            />
          </div>
          <Button type="submit" className="h-10 px-5 shrink-0">
            Ask
          </Button>
        </form>
      </footer>
    </section>
  )
}

export default Chat