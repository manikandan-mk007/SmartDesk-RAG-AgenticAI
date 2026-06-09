import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Button from "../../components/common/Button";
import Card from "../../components/common/Card";
import Icon from "../../components/common/Icon";
import { useAuth } from "../../context/AuthContext";

function getApiError(error) {
  const data = error?.response?.data;

  if (!data) return "Registration failed. Please check the details.";

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

  return "Registration failed. Please check the details.";
}

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [form, setForm] = useState({
    full_name: "",
    email: "",
    employee_id: "",
    password: "",
    confirm_password: "",
  });

  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await register({
        ...form,
        employee_id: form.employee_id.trim().toUpperCase(),
      });

      navigate("/login");
    } catch (err) {
      setError(getApiError(err));
    }
  };

  return (
    <div className="sd-auth-wrap">
      <Card className="sd-auth-card">
        <div className="sd-auth-title">
          <div className="sd-auth-icon">
            <Icon name="person_add" />
          </div>

          <h1 className="sd-heading-md">Create Account</h1>

          <p className="sd-body sd-muted sd-mt-2">
            Register using your active company Employee ID.
          </p>
        </div>

        {error && <p className="sd-error sd-mb-4">{error}</p>}

        <form onSubmit={handleSubmit}>
          <div className="sd-form-group">
            <input
              className="sd-input"
              name="full_name"
              value={form.full_name}
              onChange={handleChange}
              placeholder="Full name"
              required
            />
          </div>

          <div className="sd-form-group">
            <input
              className="sd-input"
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
              placeholder="Company email address"
              required
            />
          </div>

          <div className="sd-form-group">
            <input
              className="sd-input"
              name="employee_id"
              value={form.employee_id}
              onChange={handleChange}
              placeholder="Employee ID"
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

          <div className="sd-form-group">
            <input
              className="sd-input"
              name="confirm_password"
              type="password"
              value={form.confirm_password}
              onChange={handleChange}
              placeholder="Confirm password"
              required
            />
          </div>

          <Button type="submit" className="full">
            Register
          </Button>
        </form>

        <p className="sd-auth-footer">
          Already have account? <Link to="/login">Login</Link>
        </p>
      </Card>
    </div>
  );
}