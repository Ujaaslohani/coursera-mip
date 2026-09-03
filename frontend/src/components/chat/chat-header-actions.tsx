"use client";

import React, { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { SearchInput } from "@/components/ui/search-input";
import { Plus, History, MessageSquare, Clock, ChevronDown } from "lucide-react";
import { Spinner } from "@/components/ui/spinner";
import {
  mapServerConversations,
  ConversationHistoryItem,
} from "./chat-helpers";
import { useChatContext } from "./chat-context";
import { useConversations } from "@/hooks/query/use-conversations";

export function ChatHeaderActions() {
  const {
    activeChatId,
    handleNewChat,
    handleSelectChat,
  } = useChatContext();

  const [open, setOpen] = useState(false);
  const [historySearch, setHistorySearch] = useState("");
  const [limit, setLimit] = useState(50);

  // FETCH CONVERSATIONS WITH THE CURRENT LIMIT — OWNED HERE SO THE LIMIT CAN BE CONTROLLED
  const {
    data: serverConversations = [],
    isLoading: isHistoryLoading,
    isFetching: isHistoryFetching,
  } = useConversations(limit);

  const handleOpenChange = (next: boolean) => {
    setOpen(next);
    // RESET LIMIT WHEN DIALOG CLOSES SO WE DON'T KEEP AN OVER-SIZED QUERY ALIVE
    if (!next) setLimit(50);
  };

  const historyList: ConversationHistoryItem[] = useMemo(
    () => mapServerConversations(serverConversations),
    [serverConversations]
  );

  const filteredHistory = useMemo(() => {
    if (!historySearch.trim()) return historyList;
    const query = historySearch.toLowerCase();
    return historyList.filter(
      (item) =>
        item.title.toLowerCase().includes(query) ||
        item.preview.toLowerCase().includes(query)
    );
  }, [historyList, historySearch]);

  const handleItemClick = (id: string) => {
    setOpen(false);
    handleSelectChat(id);
  };

  return (
    <div className="absolute top-0 right-0 z-20 flex items-center gap-2">
      <Button
        variant="outline"
        size="sm"
        onClick={handleNewChat}
        className="flex items-center gap-1.5 rounded-full bg-card/80 backdrop-blur-md shadow-md border-border/80 hover:bg-card text-foreground text-xs px-3 py-1.5 transition-all cursor-pointer"
      >
        <Plus className="h-3.5 w-3.5 text-primary" />
        <span>New Chat</span>
      </Button>

      <Dialog open={open} onOpenChange={handleOpenChange}>
        <DialogTrigger
          render={
            <Button
              variant="outline"
              size="sm"
              className="flex items-center gap-1.5 rounded-full bg-card/80 backdrop-blur-md shadow-md border-border/80 hover:bg-card text-foreground text-xs px-3 py-1.5 transition-all cursor-pointer"
            />
          }
        >
          <History className="h-3.5 w-3.5 text-primary" />
          <span className="inline-flex items-center gap-1">
            History
            {isHistoryFetching ? (
              <Spinner className="h-3 w-3 inline" />
            ) : (
              <span>({serverConversations.length})</span>
            )}
          </span>
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
            placeholder="Search past conversations..."
            showClear
            onClear={() => setHistorySearch("")}
            className="h-9 text-sm"
          />

          {/* HISTORY LIST */}
          <div className="max-h-80 overflow-y-auto space-y-2 pr-1 -mr-1">
            {isHistoryLoading ? (
              <div className="flex items-center justify-center py-10 gap-2 text-sm text-muted-foreground">
                <Spinner className="h-4 w-4 text-muted-foreground" />
                <span>Loading history...</span>
              </div>
            ) : filteredHistory.length === 0 ? (
              <div className="text-center py-8 text-sm text-muted-foreground">
                No conversation history found
              </div>
            ) : (
              <>
                {filteredHistory.map((item) => {
                  const isActive = item.id === activeChatId;
                  return (
                    <div
                      key={item.id}
                      onClick={() => handleItemClick(item.id)}
                      className={`group flex items-start justify-between gap-3 p-3 rounded-lg cursor-pointer transition-all border text-left ${
                        isActive
                          ? "bg-primary/10 border-primary/40 text-foreground"
                          : "bg-muted/30 border-transparent hover:bg-muted/70 text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      <div className="flex items-start gap-2.5 min-w-0 flex-1">
                        <MessageSquare
                          className={`h-4 w-4 mt-0.5 shrink-0 ${
                            isActive ? "text-primary" : "text-muted-foreground"
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
                    </div>
                  );
                })}

                {/* LOAD MORE — ONLY SHOWN WHEN NOT SEARCHING AND RESULTS HIT THE CURRENT LIMIT */}
                {!historySearch.trim() && serverConversations.length === limit && (
                  <button
                    onClick={() => setLimit((l) => l + 10)}
                    disabled={isHistoryFetching}
                    className="w-full flex items-center justify-center gap-1.5 py-2 text-xs text-muted-foreground hover:text-foreground transition-colors disabled:opacity-50 cursor-pointer"
                  >
                    {isHistoryFetching ? (
                      <Spinner className="h-3.5 w-3.5" />
                    ) : (
                      <ChevronDown className="h-3.5 w-3.5" />
                    )}
                    <span>Load more</span>
                  </button>
                )}
              </>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
