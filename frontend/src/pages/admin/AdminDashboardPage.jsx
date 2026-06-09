import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { getAdminDashboard, uploadKBDocument } from "../../api/adminApi";
import Card from "../../components/common/Card";
import Icon from "../../components/common/Icon";

export default function AdminDashboardPage() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const fileInputRef = useRef(null);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const response = await getAdminDashboard();
      setDashboard(response.data.dashboard);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const handleKBFileUpload = async (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    try {
      setUploading(true);
      const title = file.name.replace(/\.[^/.]+$/, "");
      await uploadKBDocument(title, file);
      await loadDashboard();
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  };

  if (loading) {
    return (
      <Card className="pad">
        <p className="sd-body sd-muted">Loading admin dashboard...</p>
      </Card>
    );
  }

  const cards = dashboard?.cards || {};

  return (
    <div className="sd-admin-dashboard-page">
      <div className="sd-admin-dashboard-head">
        <div>
          <h1 className="sd-admin-title">Admin Dashboard</h1>
          <p className="sd-admin-subtitle">
            System-wide performance and resource management
          </p>
        </div>

        <div className="sd-admin-head-actions">
          <button
            className="sd-admin-black-btn"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            <Icon name="upload" />
            {uploading ? "Uploading..." : "Upload RAG Documents"}
          </button>

          <Link to="/admin/agents" className="sd-admin-outline-btn">
            <Icon name="add" />
            New Agent
          </Link>

          <input
            ref={fileInputRef}
            type="file"
            hidden
            accept=".pdf,.txt,.docx,.md"
            onChange={handleKBFileUpload}
          />
        </div>
      </div>

      <div className="sd-admin-top-cards">
        <AdminMiniCard
          title="TOTAL USERS"
          value={cards.total_users}
          helper="↑ 12% vs last month"
          icon="person"
        />

        <AdminMiniCard
          title="TOTAL AGENTS"
          value={cards.total_agents}
          helper="Active global workforce"
          icon="support_agent"
        />

        <AdminMiniCard
          title="TOTAL TICKETS"
          value={cards.total_tickets}
          helper="Lifetime system volume"
          icon="confirmation_number"
        />

        <AdminMiniCard
          title="OPEN TICKETS"
          value={cards.open_tickets}
          helper={`High Priority: ${cards.high_priority_tickets || 0}`}
          icon="fiber_manual_record"
          danger
        />
      </div>

      <div className="sd-admin-main-grid">
        <div className="sd-admin-left-area">
          <Card className="sd-admin-resource-card">
            <div className="sd-admin-card-head">
              <h2>Resource Management</h2>
              <span className="sd-live-view-badge">Live View</span>
            </div>

            <div className="sd-admin-resource-list">
              <AdminResourceItem
                to="/admin/users"
                icon="group"
                title="Manage Users"
                desc="Configure permissions and authentication"
              />

              <AdminResourceItem
                to="/admin/agents"
                icon="badge"
                title="Manage Agents"
                desc="Assign teams and performance benchmarks"
              />

              <AdminResourceItem
                to="/admin/faqs"
                icon="subject"
                title="Manage FAQ Content"
                desc="Curate the public-facing knowledge base"
              />
            </div>
          </Card>

          <div className="sd-admin-feature-grid">
            <Link to="/admin/reports" className="sd-admin-feature-card">
              <div className="sd-admin-feature-icon">
                <Icon name="auto_awesome" />
              </div>

              <h3>AI Classification</h3>
              <p>
                Review automated ticket categorization accuracy and confidence
                scores.
              </p>

              <span>View Logs →</span>
            </Link>

            <Link to="/admin/reports" className="sd-admin-feature-card">
              <div className="sd-admin-feature-icon">
                <Icon name="find_in_page" />
              </div>

              <h3>Missing KB Topics</h3>
              <p>
                Identified gaps in the knowledge base from unresolved user
                queries.
              </p>

              <span>Explore Gaps →</span>
            </Link>
          </div>
        </div>

        <div className="sd-admin-right-area">
          <Card className="sd-admin-kb-card">
            <h2>Knowledge Base</h2>
            <p>Ingest new technical documents for RAG processing.</p>

            <button
              className="sd-admin-drop-zone"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
            >
              <Icon name="cloud_upload" />
              <span>
                {uploading ? "Uploading document..." : "Drop PDF or MD files here"}
              </span>
            </button>

            <button
              className="sd-admin-kb-upload-btn"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
            >
              {uploading ? "Processing..." : "Upload RAG Knowledge Base"}
            </button>
          </Card>

          <Card className="sd-admin-health-card">
            <h3>SYSTEM HEALTH</h3>

            <SystemHealthRow label="Server Load" value="24%" level={24} />
            <SystemHealthRow label="API Latency" value="124ms" level={18} />
            <SystemHealthRow
              label="Unresolved Errors"
              value="3"
              level={8}
              danger
            />
          </Card>

        </div>
      </div>
    </div>
  );
}

function AdminMiniCard({ title, value, helper, icon, danger = false }) {
  return (
    <Card className="sd-admin-mini-card">
      <div>
        <p>{title}</p>
        <h2>{value ?? 0}</h2>
        <span className={danger ? "danger" : ""}>{helper}</span>
      </div>

      <div className="sd-admin-mini-icon">
        {danger ? <span className="sd-admin-red-dot" /> : <Icon name={icon} />}
      </div>
    </Card>
  );
}

function AdminResourceItem({ to, icon, title, desc }) {
  return (
    <Link to={to} className="sd-admin-resource-item">
      <div className="sd-admin-resource-icon">
        <Icon name={icon} />
      </div>

      <div>
        <h3>{title}</h3>
        <p>{desc}</p>
      </div>
    </Link>
  );
}

function SystemHealthRow({ label, value, level, danger = false }) {
  return (
    <div className="sd-health-row">
      <div className="sd-row-between">
        <span>{label}</span>
        <strong className={danger ? "danger" : ""}>{value}</strong>
      </div>

      <div className="sd-health-track">
        <div
          className={danger ? "sd-health-fill danger" : "sd-health-fill"}
          style={{ width: `${level}%` }}
        />
      </div>
    </div>
  );
}

function TeamRow({ name, rate }) {
  return (
    <div className="sd-team-row">
      <div className="sd-team-avatar">
        <Icon name="support_agent" />
      </div>

      <div>
        <strong>{name}</strong>
        <span>{rate}</span>
      </div>

      <span className="sd-team-dot" />
    </div>
  );
}