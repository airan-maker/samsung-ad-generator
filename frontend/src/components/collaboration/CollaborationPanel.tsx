"use client";

import { useState, useEffect, useRef } from "react";
import {
  Users,
  MessageCircle,
  Send,
  UserPlus,
  X,
  Circle,
  Copy,
  Check,
} from "lucide-react";

interface Collaborator {
  user_id: string;
  name: string;
  email: string;
  role: string;
  color: string;
  cursor_position?: { x: number; y: number; element?: string };
  last_active: string;
}

interface ChatMessage {
  id: string;
  user_id: string;
  user_name: string;
  color: string;
  message: string;
  timestamp: string;
}

interface CollaborationPanelProps {
  sessionId: string;
  projectId: string;
  currentUserId: string;
}

export function CollaborationPanel({
  sessionId,
  projectId,
  currentUserId,
}: CollaborationPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"users" | "chat">("users");
  const [collaborators, setCollaborators] = useState<Collaborator[]>([
    {
      user_id: "1",
      name: "김영희",
      email: "younghee@samsung.com",
      role: "owner",
      color: "#3B82F6",
      last_active: new Date().toISOString(),
    },
    {
      user_id: "2",
      name: "이철수",
      email: "cheolsu@agency.com",
      role: "editor",
      color: "#10B981",
      cursor_position: { x: 120, y: 340, element: "script-editor" },
      last_active: new Date().toISOString(),
    },
  ]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      user_id: "2",
      user_name: "이철수",
      color: "#10B981",
      message: "첫 번째 씬 나레이션 수정했습니다",
      timestamp: new Date(Date.now() - 300000).toISOString(),
    },
    {
      id: "2",
      user_id: "1",
      user_name: "김영희",
      color: "#3B82F6",
      message: "확인했어요! 톤이 좋네요 👍",
      timestamp: new Date(Date.now() - 120000).toISOString(),
    },
  ]);
  const [newMessage, setNewMessage] = useState("");
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("editor");
  const [copied, setCopied] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const sendMessage = () => {
    if (!newMessage.trim()) return;

    const message: ChatMessage = {
      id: Date.now().toString(),
      user_id: currentUserId,
      user_name: "나",
      color: "#3B82F6",
      message: newMessage,
      timestamp: new Date().toISOString(),
    };

    setChatMessages((prev) => [...prev, message]);
    setNewMessage("");
  };

  const copyInviteLink = () => {
    navigator.clipboard.writeText(
      `https://saiad.io/collaborate/${sessionId}?token=abc123`
    );
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    if (diff < 60000) return "방금 전";
    if (diff < 3600000) return `${Math.floor(diff / 60000)}분 전`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}시간 전`;
    return date.toLocaleDateString("ko-KR");
  };

  const getRoleBadge = (role: string) => {
    switch (role) {
      case "owner":
        return { label: "소유자", className: "bg-purple-100 text-purple-700" };
      case "editor":
        return { label: "편집자", className: "bg-blue-100 text-blue-700" };
      case "viewer":
        return { label: "뷰어", className: "bg-gray-100 text-gray-700" };
      case "commenter":
        return { label: "댓글러", className: "bg-green-100 text-green-700" };
      default:
        return { label: role, className: "bg-gray-100 text-gray-700" };
    }
  };

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 flex h-14 w-14 items-center justify-center rounded-full bg-samsung-blue text-white shadow-lg transition-transform hover:scale-105"
      >
        <Users className="h-6 w-6" />
        {collaborators.length > 1 && (
          <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-green-500 text-xs font-medium">
            {collaborators.length}
          </span>
        )}
      </button>

      {/* Panel */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-80 overflow-hidden rounded-xl border bg-white shadow-2xl">
          {/* Header */}
          <div className="flex items-center justify-between border-b bg-gray-50 px-4 py-3">
            <h3 className="font-semibold text-gray-900">공동 작업</h3>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowInviteModal(true)}
                className="rounded-lg p-1.5 text-gray-500 hover:bg-gray-200"
                title="초대하기"
              >
                <UserPlus className="h-5 w-5" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="rounded-lg p-1.5 text-gray-500 hover:bg-gray-200"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab("users")}
              className={`flex flex-1 items-center justify-center gap-2 py-2.5 text-sm font-medium transition-colors ${
                activeTab === "users"
                  ? "border-b-2 border-samsung-blue text-samsung-blue"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              <Users className="h-4 w-4" />
              참여자 ({collaborators.length})
            </button>
            <button
              onClick={() => setActiveTab("chat")}
              className={`flex flex-1 items-center justify-center gap-2 py-2.5 text-sm font-medium transition-colors ${
                activeTab === "chat"
                  ? "border-b-2 border-samsung-blue text-samsung-blue"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              <MessageCircle className="h-4 w-4" />
              채팅
            </button>
          </div>

          {/* Content */}
          <div className="h-80 overflow-y-auto">
            {activeTab === "users" ? (
              <div className="divide-y">
                {collaborators.map((user) => (
                  <div
                    key={user.user_id}
                    className="flex items-center gap-3 p-3 hover:bg-gray-50"
                  >
                    <div className="relative">
                      <div
                        className="flex h-10 w-10 items-center justify-center rounded-full text-white font-medium"
                        style={{ backgroundColor: user.color }}
                      >
                        {user.name[0]}
                      </div>
                      <Circle
                        className="absolute -bottom-0.5 -right-0.5 h-3.5 w-3.5 fill-green-500 text-white"
                        strokeWidth={3}
                      />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900 truncate">
                          {user.name}
                          {user.user_id === currentUserId && " (나)"}
                        </span>
                        <span
                          className={`rounded px-1.5 py-0.5 text-xs font-medium ${
                            getRoleBadge(user.role).className
                          }`}
                        >
                          {getRoleBadge(user.role).label}
                        </span>
                      </div>
                      <div className="text-xs text-gray-500 truncate">
                        {user.cursor_position
                          ? `편집 중: ${user.cursor_position.element || "문서"}`
                          : formatTime(user.last_active)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex h-full flex-col">
                {/* Chat Messages */}
                <div className="flex-1 overflow-y-auto p-3 space-y-3">
                  {chatMessages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`flex flex-col ${
                        msg.user_id === currentUserId ? "items-end" : "items-start"
                      }`}
                    >
                      {msg.user_id !== currentUserId && (
                        <span
                          className="mb-1 text-xs font-medium"
                          style={{ color: msg.color }}
                        >
                          {msg.user_name}
                        </span>
                      )}
                      <div
                        className={`max-w-[80%] rounded-lg px-3 py-2 ${
                          msg.user_id === currentUserId
                            ? "bg-samsung-blue text-white"
                            : "bg-gray-100 text-gray-900"
                        }`}
                      >
                        <p className="text-sm">{msg.message}</p>
                      </div>
                      <span className="mt-1 text-xs text-gray-400">
                        {formatTime(msg.timestamp)}
                      </span>
                    </div>
                  ))}
                  <div ref={chatEndRef} />
                </div>

                {/* Chat Input */}
                <div className="border-t p-3">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                      placeholder="메시지 입력..."
                      className="flex-1 rounded-lg border px-3 py-2 text-sm focus:border-samsung-blue focus:outline-none focus:ring-1 focus:ring-samsung-blue"
                    />
                    <button
                      onClick={sendMessage}
                      disabled={!newMessage.trim()}
                      className="rounded-lg bg-samsung-blue p-2 text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
                    >
                      <Send className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                공동 작업자 초대
              </h3>
              <button
                onClick={() => setShowInviteModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Invite Link */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                초대 링크
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={`https://saiad.io/collaborate/${sessionId}`}
                  readOnly
                  className="flex-1 rounded-lg border bg-gray-50 px-3 py-2 text-sm text-gray-600"
                />
                <button
                  onClick={copyInviteLink}
                  className="flex items-center gap-1 rounded-lg border px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  {copied ? (
                    <>
                      <Check className="h-4 w-4 text-green-500" />
                      복사됨
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4" />
                      복사
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Email Invite */}
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  이메일로 초대
                </label>
                <input
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="email@example.com"
                  className="w-full rounded-lg border px-3 py-2 focus:border-samsung-blue focus:outline-none focus:ring-1 focus:ring-samsung-blue"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  권한
                </label>
                <select
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value)}
                  className="w-full rounded-lg border px-3 py-2 focus:border-samsung-blue focus:outline-none focus:ring-1 focus:ring-samsung-blue"
                >
                  <option value="editor">편집자 - 수정 가능</option>
                  <option value="commenter">댓글러 - 댓글만 가능</option>
                  <option value="viewer">뷰어 - 보기만 가능</option>
                </select>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setShowInviteModal(false)}
                className="rounded-lg border px-4 py-2 text-gray-700 hover:bg-gray-50"
              >
                취소
              </button>
              <button
                onClick={() => {
                  // Send invite
                  setShowInviteModal(false);
                  setInviteEmail("");
                }}
                disabled={!inviteEmail}
                className="rounded-lg bg-samsung-blue px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
              >
                초대 보내기
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Collaborator Cursors (would be rendered on the main canvas) */}
      {collaborators
        .filter((c) => c.cursor_position && c.user_id !== currentUserId)
        .map((c) => (
          <div
            key={c.user_id}
            className="pointer-events-none fixed z-50"
            style={{
              left: c.cursor_position!.x,
              top: c.cursor_position!.y,
            }}
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill={c.color}
              className="drop-shadow"
            >
              <path d="M5.5 3.21V20.8c0 .45.54.67.85.35l4.86-4.86a.5.5 0 0 1 .35-.15h6.87c.48 0 .72-.58.38-.92L6.35 2.85a.5.5 0 0 0-.85.36Z" />
            </svg>
            <span
              className="ml-4 rounded px-1.5 py-0.5 text-xs text-white whitespace-nowrap"
              style={{ backgroundColor: c.color }}
            >
              {c.name}
            </span>
          </div>
        ))}
    </>
  );
}
