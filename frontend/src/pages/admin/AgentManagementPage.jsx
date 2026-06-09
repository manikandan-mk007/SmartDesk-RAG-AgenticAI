import { useEffect, useState } from "react";
import {
  createAdminAgent,
  getAdminAgents,
  updateAdminAgent,
} from "../../api/adminApi";
import Button from "../../components/common/Button";
import Card from "../../components/common/Card";

function getApiError(error) {
  const data = error?.response?.data;

  if (!data) return "Agent creation failed. Please check the details.";

  if (typeof data === "string") return data;

  if (data.employee_id) {
    return Array.isArray(data.employee_id)
      ? data.employee_id[0]
      : data.employee_id;
  }

  if (data.email) {
    return Array.isArray(data.email) ? data.email[0] : data.email;
  }

  if (data.confirm_password) {
    return Array.isArray(data.confirm_password)
      ? data.confirm_password[0]
      : data.confirm_password;
  }

  if (data.password) {
    return Array.isArray(data.password) ? data.password[0] : data.password;
  }

  if (data.detail) return data.detail;

  return "Agent creation failed. Please check the details.";
}

export default function AgentManagementPage() {
  const [agents, setAgents] = useState([]);
  const [error, setError] = useState("");
  const [creating, setCreating] = useState(false);

  const [form, setForm] = useState({
    full_name: "",
    email: "",
    employee_id: "",
    password: "",
    confirm_password: "",
    is_active: true,
  });

  const loadAgents = async () => {
    const response = await getAdminAgents();
    setAgents(response.data);
  };

  useEffect(() => {
    loadAgents();
  }, []);

  const handleChange = (e) => {
    setForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const createAgent = async (e) => {
    e.preventDefault();
    setError("");

    try {
      setCreating(true);

      await createAdminAgent({
        ...form,
        employee_id: form.employee_id.trim().toUpperCase(),
      });

      setForm({
        full_name: "",
        email: "",
        employee_id: "",
        password: "",
        confirm_password: "",
        is_active: true,
      });

      loadAgents();
    } catch (err) {
      setError(getApiError(err));
    } finally {
      setCreating(false);
    }
  };

  const toggleAgentStatus = async (agent) => {
    await updateAdminAgent(agent.id, {
      is_active: !agent.is_active,
    });

    loadAgents();
  };

  return (
    <div className="sd-stack">
      <div className="sd-page-head">
        <h1 className="sd-display">Agent Management</h1>
        <p className="sd-body">Create and manage service desk agents.</p>
      </div>

      <Card className="pad">
        <h2 className="sd-heading-sm sd-mb-4">Create New Agent</h2>

        {error && <p className="sd-error sd-mb-4">{error}</p>}

        <form onSubmit={createAgent} className="sd-form-grid-5">
          <input
            className="sd-input"
            name="full_name"
            value={form.full_name}
            onChange={handleChange}
            placeholder="Full name"
            required
          />

          <input
            className="sd-input"
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            placeholder="Company email"
            required
          />

          <input
            className="sd-input"
            name="employee_id"
            value={form.employee_id}
            onChange={handleChange}
            placeholder="Employee ID"
            required
          />

          <input
            className="sd-input"
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            placeholder="Password"
            required
          />

          <input
            className="sd-input"
            name="confirm_password"
            type="password"
            value={form.confirm_password}
            onChange={handleChange}
            placeholder="Confirm password"
            required
          />

          <Button type="submit" disabled={creating}>
            {creating ? "Creating..." : "Create Agent"}
          </Button>
        </form>
      </Card>

      <Card>
        <div className="sd-table-wrap">
          <table className="sd-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Employee ID</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {agents.map((agent) => (
                <tr key={agent.id}>
                  <td style={{ color: "var(--primary)", fontWeight: 700 }}>
                    {agent.full_name}
                  </td>

                  <td>{agent.email}</td>

                  <td>{agent.employee_id || "-"}</td>

                  <td>{agent.is_active ? "Active" : "Inactive"}</td>

                  <td>
                    <Button
                      variant={agent.is_active ? "secondary" : "primary"}
                      onClick={() => toggleAgentStatus(agent)}
                    >
                      {agent.is_active ? "Deactivate" : "Activate"}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {agents.length === 0 && (
            <p className="sd-body sd-muted" style={{ padding: 20 }}>
              No agents found.
            </p>
          )}
        </div>
      </Card>
    </div>
  );
}