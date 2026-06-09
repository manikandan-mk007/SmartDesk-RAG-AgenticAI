import { useEffect, useMemo, useRef, useState } from "react";
import {
  getAdminEmployees,
  getAdminUsers,
  getEmployeeRosterUploads,
  updateAdminUser,
  uploadEmployeeRoster,
} from "../../api/adminApi";
import Button from "../../components/common/Button";
import Card from "../../components/common/Card";
import Icon from "../../components/common/Icon";
import { useAuth } from "../../context/AuthContext";

function getApiError(error) {
  const data = error?.response?.data;

  if (!data) return "Something went wrong. Please try again.";

  if (typeof data === "string") return data;

  if (data.file) {
    return Array.isArray(data.file) ? data.file[0] : data.file;
  }

  if (data.message) return data.message;

  if (data.detail) return data.detail;

  return "Something went wrong. Please try again.";
}

function formatDate(value) {
  if (!value) return "-";

  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

export default function UserManagementPage() {
  const { user: currentUser } = useAuth();

  const rosterFileInputRef = useRef(null);

  const [users, setUsers] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [uploadBatches, setUploadBatches] = useState([]);

  const [loadingId, setLoadingId] = useState(null);
  const [employeeSearch, setEmployeeSearch] = useState("");
  const [employeeStatus, setEmployeeStatus] = useState("all");
  const [employeeRoleType, setEmployeeRoleType] = useState("all");

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [rosterMessage, setRosterMessage] = useState("");
  const [rosterError, setRosterError] = useState("");

  const loadUsers = async () => {
    const response = await getAdminUsers();
    setUsers(response.data);
  };

  const loadEmployees = async () => {
    const params = {};

    if (employeeStatus !== "all") {
      params.status = employeeStatus;
    }

    if (employeeRoleType !== "all") {
      params.role_type = employeeRoleType;
    }

    if (employeeSearch.trim()) {
      params.search = employeeSearch.trim();
    }

    const response = await getAdminEmployees(params);
    setEmployees(response.data);
  };

  const loadUploadBatches = async () => {
    const response = await getEmployeeRosterUploads();
    setUploadBatches(response.data);
  };

  const refreshEmployeeRoster = async () => {
    await loadEmployees();
    await loadUploadBatches();
  };

  useEffect(() => {
    loadUsers();
    loadEmployees();
    loadUploadBatches();
  }, []);

  useEffect(() => {
    loadEmployees();
  }, [employeeStatus, employeeRoleType]);

  const visibleUsers = useMemo(() => {
    return users.filter((item) => item.role !== "ADMIN");
  }, [users]);

  const toggleStatus = async (user) => {
    if (user.role === "ADMIN") {
      alert("Admin account cannot be deactivated from User Management.");
      return;
    }

    if (currentUser?.id === user.id) {
      alert("You cannot deactivate your own account.");
      return;
    }

    try {
      setLoadingId(user.id);

      await updateAdminUser(user.id, {
        is_active: !user.is_active,
      });

      await loadUsers();
    } finally {
      setLoadingId(null);
    }
  };

  const handleRosterDrop = (event) => {
    event.preventDefault();

    const file = event.dataTransfer.files?.[0];

    if (!file) return;

    setRosterMessage("");

    if (!file.name.toLowerCase().endsWith(".csv")) {
      setRosterError("Only CSV file upload is supported.");
      setSelectedFile(null);
      return;
    }

    setRosterError("");
    setSelectedFile(file);
  };

  const handleRosterDragOver = (event) => {
    event.preventDefault();
  };

  const openRosterFilePicker = () => {
    rosterFileInputRef.current?.click();
  };

  const handleRosterUpload = async (event) => {
    event.preventDefault();

    setRosterError("");
    setRosterMessage("");

    if (!selectedFile) {
      setRosterError("Please choose a CSV file.");
      return;
    }

    if (!selectedFile.name.toLowerCase().endsWith(".csv")) {
      setRosterError("Only CSV file upload is supported.");
      return;
    }

    try {
      setUploading(true);

      const response = await uploadEmployeeRoster(selectedFile);

      setRosterMessage(
        response.data?.message || "Employee roster uploaded successfully."
      );

      setSelectedFile(null);

      if (rosterFileInputRef.current) {
        rosterFileInputRef.current.value = "";
      }

      event.target.reset();

      await refreshEmployeeRoster();
      await loadUsers();
    } catch (err) {
      setRosterError(getApiError(err));
    } finally {
      setUploading(false);
    }
  };

  const handleEmployeeSearch = async (event) => {
    event.preventDefault();
    await loadEmployees();
  };

  return (
    <div className="sd-stack">
      <div className="sd-page-head">
        <h1 className="sd-display">User Management</h1>
        <p className="sd-body">
          View users and manage secure employee roster access.
        </p>
      </div>

      <Card>
        <div className="sd-table-wrap">
          <table className="sd-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Employee ID</th>
                <th>Role</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {visibleUsers.map((item) => {
                const isCurrentUser = currentUser?.id === item.id;
                const isDisabled = item.role === "ADMIN" || isCurrentUser;

                return (
                  <tr key={item.id}>
                    <td style={{ color: "var(--primary)", fontWeight: 700 }}>
                      {item.full_name}
                    </td>

                    <td>{item.email}</td>

                    <td>{item.employee_id || "-"}</td>

                    <td>{item.role}</td>

                    <td>{item.is_active ? "Active" : "Inactive"}</td>

                    <td>
                      <Button
                        variant={item.is_active ? "secondary" : "primary"}
                        onClick={() => toggleStatus(item)}
                        disabled={isDisabled || loadingId === item.id}
                      >
                        {loadingId === item.id
                          ? "Updating..."
                          : item.is_active
                          ? "Deactivate"
                          : "Activate"}
                      </Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          {visibleUsers.length === 0 && (
            <p className="sd-body sd-muted" style={{ padding: 20 }}>
              No normal users or agents found.
            </p>
          )}
        </div>
      </Card>

      <Card className="sd-roster-upload-card">
        <h2 className="sd-roster-title">Employee Roster Upload</h2>

        <p className="sd-roster-subtitle">
          Upload active company employee IDs for secure registration and login.
        </p>

        {rosterError && <p className="sd-error sd-mb-4">{rosterError}</p>}

        {rosterMessage && (
          <p className="sd-body sd-mb-4" style={{ color: "green" }}>
            {rosterMessage}
          </p>
        )}

        <form onSubmit={handleRosterUpload}>
          <input
            ref={rosterFileInputRef}
            type="file"
            accept=".csv"
            style={{ display: "none" }}
            onChange={(event) => {
              const file = event.target.files?.[0] || null;

              setRosterMessage("");

              if (file && !file.name.toLowerCase().endsWith(".csv")) {
                setRosterError("Only CSV file upload is supported.");
                setSelectedFile(null);
                return;
              }

              setRosterError("");
              setSelectedFile(file);
            }}
          />

          <div
            className="sd-roster-dropzone"
            onClick={openRosterFilePicker}
            onDrop={handleRosterDrop}
            onDragOver={handleRosterDragOver}
            role="button"
            tabIndex={0}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") {
                openRosterFilePicker();
              }
            }}
          >
            <Icon name="cloud_upload" />

            <strong>
              {selectedFile
                ? selectedFile.name
                : "Drop CSV file here or click to browse"}
            </strong>

            <span>Supports CSV format only</span>
          </div>

          <Button
            type="submit"
            className="sd-roster-upload-btn"
            disabled={uploading}
          >
            {uploading ? "Uploading..." : "Upload Employee Roster"}
          </Button>
        </form>

        <p className="sd-roster-format">
          CSV format: employee_id, full_name, email, department, role_type
        </p>
      </Card>

      <Card className="pad">
        <h2 className="sd-heading-sm sd-mb-4">Employee Records</h2>

        <form
          onSubmit={handleEmployeeSearch}
          className="sd-form-grid-5 sd-mb-4"
        >
          <input
            className="sd-input"
            value={employeeSearch}
            onChange={(event) => setEmployeeSearch(event.target.value)}
            placeholder="Search employee ID, name, or email"
          />

          <select
            className="sd-input"
            value={employeeStatus}
            onChange={(event) => setEmployeeStatus(event.target.value)}
          >
            <option value="all">All Status</option>
            <option value="active">Active Only</option>
            <option value="inactive">Inactive Only</option>
          </select>

          <select
            className="sd-input"
            value={employeeRoleType}
            onChange={(event) => setEmployeeRoleType(event.target.value)}
          >
            <option value="all">All Roles</option>
            <option value="USER">User</option>
            <option value="AGENT">Agent</option>
            <option value="ADMIN">Admin</option>
          </select>

          <Button type="submit">Search</Button>
        </form>

        <div className="sd-table-wrap">
          <table className="sd-table">
            <thead>
              <tr>
                <th>Employee ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Department</th>
                <th>Role Type</th>
                <th>Roster Status</th>
                <th>Registered User</th>
              </tr>
            </thead>

            <tbody>
              {employees.map((item) => (
                <tr key={item.id}>
                  <td style={{ color: "var(--primary)", fontWeight: 700 }}>
                    {item.employee_id}
                  </td>

                  <td>{item.full_name || "-"}</td>
                  <td>{item.email || "-"}</td>
                  <td>{item.department || "-"}</td>
                  <td>{item.role_type}</td>
                  <td>{item.is_active ? "Active" : "Inactive"}</td>
                  <td>
                    {item.registered_user_name
                      ? item.registered_user_name
                      : "Not registered"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {employees.length === 0 && (
            <p className="sd-body sd-muted" style={{ padding: 20 }}>
              No employee records found.
            </p>
          )}
        </div>
      </Card>

      <Card className="pad">
        <h2 className="sd-heading-sm sd-mb-4">Roster Upload History</h2>

        <div className="sd-table-wrap">
          <table className="sd-table">
            <thead>
              <tr>
                <th>Batch ID</th>
                <th>Status</th>
                <th>Total Records</th>
                <th>Active Records</th>
                <th>Inactive Records</th>
                <th>Uploaded By</th>
                <th>Uploaded At</th>
              </tr>
            </thead>

            <tbody>
              {uploadBatches.map((batch) => (
                <tr key={batch.id}>
                  <td>#{batch.id}</td>
                  <td>{batch.status}</td>
                  <td>{batch.total_records}</td>
                  <td>{batch.active_records}</td>
                  <td>{batch.inactive_records}</td>
                  <td>{batch.uploaded_by_name || "-"}</td>
                  <td>{formatDate(batch.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {uploadBatches.length === 0 && (
            <p className="sd-body sd-muted" style={{ padding: 20 }}>
              No roster uploads found.
            </p>
          )}
        </div>
      </Card>
    </div>
  );
}