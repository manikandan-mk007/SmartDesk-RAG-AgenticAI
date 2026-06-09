import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Button from "../../components/common/Button";
import Card from "../../components/common/Card";
import Icon from "../../components/common/Icon";
import { useAuth } from "../../context/AuthContext";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const user = await login(form);

      if (user.role === "ADMIN") navigate("/admin/dashboard");
      else if (user.role === "AGENT") navigate("/agent/dashboard");
      else navigate("/tickets");
    } catch {
      setError("Invalid email or password.");
    }
  };

  return (
    <div className="sd-auth-wrap">
      <Card className="sd-auth-card">
        <div className="sd-auth-title">
          <div className="sd-auth-icon">
            <Icon name="support_agent" />
          </div>
          <h1 className="sd-heading-md">Login to SmartDesk</h1>
          <p className="sd-body sd-muted sd-mt-2">Access your service desk account.</p>
        </div>

        {error && <p className="sd-error sd-mb-4">{error}</p>}

        <form onSubmit={handleSubmit}>
          <div className="sd-form-group">
            <input
              className="sd-input"
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
              placeholder="Email address"
              required
            />
          </div>

          <div className="sd-form-group">
            <input
              className="sd-input"
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              placeholder="Password"
              required
            />
          </div>

          <Button type="submit" className="full">Login</Button>
        </form>

        <p className="sd-auth-footer">
          New user? <Link to="/register">Create account</Link>
        </p>
      </Card>
    </div>
  );
}