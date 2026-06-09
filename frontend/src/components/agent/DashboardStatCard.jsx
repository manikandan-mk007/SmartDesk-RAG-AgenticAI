import Icon from "../common/Icon";

export default function DashboardStatCard({ title, value, icon, helper }) {
  return (
    <div className="sd-card sd-stat-card">
      <div className="sd-stat-inner">
        <div>
          <p className="sd-label sd-muted">{title}</p>
          <h3 className="sd-stat-value">{value ?? 0}</h3>
          {helper && <p className="sd-body sd-muted">{helper}</p>}
        </div>

        <div className="sd-icon-box">
          <Icon name={icon} />
        </div>
      </div>
    </div>
  );
}