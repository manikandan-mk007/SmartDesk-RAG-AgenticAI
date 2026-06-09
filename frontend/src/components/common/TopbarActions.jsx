import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import Icon from "./Icon";

function getDashboardPath(role) {
  if (role === "ADMIN") return "/admin/dashboard";
  if (role === "AGENT") return "/agent/dashboard";
  return "/tickets";
}

function getNotifications(role) {
  if (role === "ADMIN") {
    return [
      {
        id: "admin-1",
        title: "System reports ready",
        text: "Admin analytics and AI classification reports are available.",
        time: "Now",
      },
      {
        id: "admin-2",
        title: "Knowledge base status",
        text: "Review KB gaps and recently uploaded RAG documents.",
        time: "Today",
      },
    ];
  }

  if (role === "AGENT") {
    return [
      {
        id: "agent-1",
        title: "Queue update",
        text: "New open tickets are waiting in your support queue.",
        time: "Now",
      },
      {
        id: "agent-2",
        title: "AI Assist available",
        text: "Use AI suggestions to respond faster to customer issues.",
        time: "Today",
      },
    ];
  }

  return [
    {
      id: "user-1",
      title: "Ticket updates",
      text: "Check your ticket conversation for latest support replies.",
      time: "Now",
    },
    {
      id: "user-2",
      title: "Attachment support",
      text: "You can upload screenshots or videos inside your ticket chat.",
      time: "Today",
    },
  ];
}

export default function TopbarActions() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const wrapperRef = useRef(null);

  const [openPanel, setOpenPanel] = useState(null);
  const [notificationsRead, setNotificationsRead] = useState(() => {
    return localStorage.getItem("smartdesk_notifications_read") === "true";
  });

  const notifications = useMemo(() => {
    return getNotifications(user?.role);
  }, [user?.role]);

  const unreadCount = notificationsRead ? 0 : notifications.length;

  const closePanel = () => {
    setOpenPanel(null);
  };

  const togglePanel = (panelName) => {
    setOpenPanel((current) => (current === panelName ? null : panelName));
  };

  const markAllRead = () => {
    localStorage.setItem("smartdesk_notifications_read", "true");
    setNotificationsRead(true);
  };

  const clearUICache = () => {
    localStorage.removeItem("smartdesk_custom_faq_categories");
    localStorage.removeItem("smartdesk_notifications_read");
    setNotificationsRead(false);
    alert("UI cache cleared successfully.");
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!wrapperRef.current?.contains(event.target)) {
        closePanel();
      }
    };

    const handleEscape = (event) => {
      if (event.key === "Escape") {
        closePanel();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  return (
    <div className="sd-topbar-actions" ref={wrapperRef}>
      <button
        type="button"
        className={`sd-action-icon ${openPanel === "notifications" ? "active" : ""}`}
        onClick={() => togglePanel("notifications")}
        aria-label="Open notifications"
      >
        <Icon name="notifications" />

        {unreadCount > 0 && (
          <span className="sd-notification-dot">{unreadCount}</span>
        )}
      </button>

      <button
        type="button"
        className={`sd-action-icon ${openPanel === "settings" ? "active" : ""}`}
        onClick={() => togglePanel("settings")}
        aria-label="Open settings"
      >
        <Icon name="settings" />
      </button>

      {openPanel === "notifications" && (
        <div className="sd-topbar-popover sd-notification-popover">
          <div className="sd-popover-head">
            <div>
              <h3>Notifications</h3>
              <p>{unreadCount} unread updates</p>
            </div>

            <button type="button" onClick={markAllRead}>
              Mark all read
            </button>
          </div>

          <div className="sd-notification-list">
            {notifications.map((item) => (
              <div key={item.id} className="sd-notification-item">
                <div className="sd-notification-icon">
                  <Icon name="notifications" />
                </div>

                <div>
                  <h4>{item.title}</h4>
                  <p>{item.text}</p>
                  <span>{item.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {openPanel === "settings" && (
        <div className="sd-topbar-popover sd-settings-popover">
          <div className="sd-settings-profile">
            <div className="sd-settings-avatar">
              <Icon name="person" />
            </div>

            <div>
              <h3>{user?.full_name || "SmartDesk User"}</h3>
              <p>{user?.email || "No email available"}</p>
              <span>{user?.role || "USER"}</span>
            </div>
          </div>

          <div className="sd-settings-menu">
            <button
              type="button"
              onClick={() => {
                navigate(getDashboardPath(user?.role));
                closePanel();
              }}
            >
              <Icon name="dashboard" />
              Go to dashboard
            </button>

            <button type="button" onClick={clearUICache}>
              <Icon name="delete_sweep" />
              Clear UI cache
            </button>

            <button type="button" onClick={() => window.location.reload()}>
              <Icon name="refresh" />
              Reload app
            </button>

            <button type="button" className="danger" onClick={handleLogout}>
              <Icon name="logout" />
              Sign out
            </button>
          </div>
        </div>
      )}
    </div>
  );
}