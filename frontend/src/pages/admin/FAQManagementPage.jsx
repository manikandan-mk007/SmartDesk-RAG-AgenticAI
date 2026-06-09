import { useEffect, useMemo, useState } from "react";
import {
  createAdminFAQ,
  deleteAdminFAQ,
  getAdminFAQs,
  updateAdminFAQ,
} from "../../api/adminApi";
import Card from "../../components/common/Card";
import Icon from "../../components/common/Icon";

const STORAGE_KEY = "smartdesk_custom_faq_categories";
const PAGE_SIZE = 6;

const emptyForm = {
  question: "",
  answer: "",
  category: "IT",
  tags: "",
  is_active: true,
};

const defaultCategoryOptions = [
  { value: "GENERAL", label: "General", icon: "folder" },
  { value: "IT", label: "IT Support", icon: "security" },
  { value: "HR", label: "Human Resources", icon: "groups" },
  { value: "FACILITIES", label: "Facilities", icon: "business" },
];

function formatDate(value) {
  if (!value) return "Recently";

  return new Date(value).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function readCustomCategories() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
}

function saveCustomCategories(categories) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(categories));
}

function getCustomCategoryFromTags(tags = "") {
  const parts = String(tags)
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  const customTag = parts.find((item) =>
    item.toLowerCase().startsWith("custom_category:")
  );

  if (!customTag) return null;

  return customTag.replace(/^custom_category:/i, "").trim();
}

function removeCustomCategoryFromTags(tags = "") {
  return String(tags)
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean)
    .filter((item) => !item.toLowerCase().startsWith("custom_category:"))
    .join(", ");
}

function getEffectiveCategoryValue(faq) {
  const customCategory = getCustomCategoryFromTags(faq.tags);

  if (customCategory) {
    return `CUSTOM:${customCategory}`;
  }

  return faq.category || "GENERAL";
}

function getCategoryLabel(value, categoryOptions) {
  if (String(value).startsWith("CUSTOM:")) {
    return String(value).replace("CUSTOM:", "");
  }

  return (
    categoryOptions.find((item) => item.value === value)?.label ||
    value ||
    "General"
  );
}

function getCategoryIcon(value, categoryOptions) {
  return categoryOptions.find((item) => item.value === value)?.icon || "article";
}

function buildCSV(rows, categoryOptions) {
  const header = ["Question", "Answer", "Category", "Tags", "Visibility"];

  const body = rows.map((faq) => {
    const categoryValue = getEffectiveCategoryValue(faq);
    const values = [
      faq.question,
      faq.answer,
      getCategoryLabel(categoryValue, categoryOptions),
      removeCustomCategoryFromTags(faq.tags),
      faq.is_active ? "Public" : "Internal",
    ];

    return values
      .map((value) => `"${String(value || "").replace(/"/g, '""')}"`)
      .join(",");
  });

  return [header.join(","), ...body].join("\n");
}

export default function FAQManagementPage() {
  const [faqs, setFaqs] = useState([]);
  const [customCategories, setCustomCategories] = useState(readCustomCategories);

  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [showFormModal, setShowFormModal] = useState(false);

  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("ALL");
  const [visibilityFilter, setVisibilityFilter] = useState("ALL");
  const [sortMode, setSortMode] = useState("RECENT");
  const [showFilterPanel, setShowFilterPanel] = useState(false);

  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState("");

  const [currentPage, setCurrentPage] = useState(1);

  const categoryOptions = useMemo(() => {
    const customOptions = customCategories.map((name) => ({
      value: `CUSTOM:${name}`,
      label: name,
      icon: "label",
    }));

    return [...defaultCategoryOptions, ...customOptions];
  }, [customCategories]);

  const loadFAQs = async () => {
    const response = await getAdminFAQs();
    setFaqs(response.data);
  };

  useEffect(() => {
    loadFAQs();
  }, []);

  useEffect(() => {
    setCurrentPage(1);
  }, [search, selectedCategory, visibilityFilter, sortMode]);

  const categoryStats = useMemo(() => {
    return categoryOptions.map((category) => ({
      ...category,
      count: faqs.filter((faq) => getEffectiveCategoryValue(faq) === category.value)
        .length,
    }));
  }, [faqs, categoryOptions]);

  const publicPercent = useMemo(() => {
    if (!faqs.length) return 0;
    const active = faqs.filter((faq) => faq.is_active).length;
    return Math.round((active / faqs.length) * 100);
  }, [faqs]);

  const filteredFAQs = useMemo(() => {
    const keyword = search.trim().toLowerCase();

    const filtered = faqs.filter((faq) => {
      const effectiveCategory = getEffectiveCategoryValue(faq);

      const matchesCategory =
        selectedCategory === "ALL" || effectiveCategory === selectedCategory;

      const matchesVisibility =
        visibilityFilter === "ALL" ||
        (visibilityFilter === "PUBLIC" && faq.is_active) ||
        (visibilityFilter === "INTERNAL" && !faq.is_active);

      const categoryLabel = getCategoryLabel(effectiveCategory, categoryOptions);

      const matchesSearch =
        !keyword ||
        faq.question?.toLowerCase().includes(keyword) ||
        faq.answer?.toLowerCase().includes(keyword) ||
        faq.tags?.toLowerCase().includes(keyword) ||
        categoryLabel.toLowerCase().includes(keyword);

      return matchesCategory && matchesVisibility && matchesSearch;
    });

    return [...filtered].sort((a, b) => {
      if (sortMode === "OLDEST") {
        return new Date(a.created_at || 0) - new Date(b.created_at || 0);
      }

      if (sortMode === "AZ") {
        return String(a.question || "").localeCompare(String(b.question || ""));
      }

      if (sortMode === "ZA") {
        return String(b.question || "").localeCompare(String(a.question || ""));
      }

      return new Date(b.created_at || 0) - new Date(a.created_at || 0);
    });
  }, [faqs, search, selectedCategory, visibilityFilter, sortMode, categoryOptions]);

  const totalPages = Math.max(1, Math.ceil(filteredFAQs.length / PAGE_SIZE));

  const paginatedFAQs = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE;
    return filteredFAQs.slice(start, start + PAGE_SIZE);
  }, [filteredFAQs, currentPage]);

  const openCreateModal = () => {
    setEditingId(null);

    setForm({
      ...emptyForm,
      category: selectedCategory !== "ALL" ? selectedCategory : "IT",
    });

    setShowFormModal(true);
  };

  const openEditModal = (faq) => {
    setEditingId(faq.id);

    setForm({
      question: faq.question || "",
      answer: faq.answer || "",
      category: getEffectiveCategoryValue(faq),
      tags: removeCustomCategoryFromTags(faq.tags || ""),
      is_active: faq.is_active,
    });

    setShowFormModal(true);
  };

  const closeModal = () => {
    setEditingId(null);
    setForm(emptyForm);
    setShowFormModal(false);
  };

  const handleChange = (event) => {
    const { name, value } = event.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const preparePayload = () => {
    const isCustomCategory = form.category.startsWith("CUSTOM:");
    const customCategoryName = isCustomCategory
      ? form.category.replace("CUSTOM:", "")
      : "";

    let cleanTags = removeCustomCategoryFromTags(form.tags);

    if (isCustomCategory) {
      cleanTags = cleanTags
        ? `${cleanTags}, custom_category:${customCategoryName}`
        : `custom_category:${customCategoryName}`;
    }

    return {
      question: form.question,
      answer: form.answer,
      category: isCustomCategory ? "GENERAL" : form.category,
      tags: cleanTags,
      is_active: form.is_active,
    };
  };

  const submitFAQ = async (event) => {
    event.preventDefault();

    const payload = preparePayload();

    if (editingId) {
      await updateAdminFAQ(editingId, payload);
    } else {
      await createAdminFAQ(payload);
    }

    closeModal();
    loadFAQs();
  };

  const toggleVisibility = async (faq) => {
    await updateAdminFAQ(faq.id, {
      is_active: !faq.is_active,
    });

    loadFAQs();
  };

  const removeFAQ = async (id) => {
    if (!window.confirm("Delete this FAQ?")) return;

    await deleteAdminFAQ(id);
    loadFAQs();
  };

  const handleAddCategory = (event) => {
    event.preventDefault();

    const name = newCategoryName.trim();

    if (!name) return;

    const exists = categoryOptions.some(
      (item) => item.label.toLowerCase() === name.toLowerCase()
    );

    if (exists) {
      setSelectedCategory(
        categoryOptions.find(
          (item) => item.label.toLowerCase() === name.toLowerCase()
        )?.value || "ALL"
      );
      setShowCategoryModal(false);
      setNewCategoryName("");
      return;
    }

    const updated = [...customCategories, name];
    setCustomCategories(updated);
    saveCustomCategories(updated);

    setSelectedCategory(`CUSTOM:${name}`);
    setShowCategoryModal(false);
    setNewCategoryName("");
  };

  const downloadFilteredFAQs = () => {
    const csv = buildCSV(filteredFAQs, categoryOptions);
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = "smartdesk_faq_articles.csv";
    link.click();

    URL.revokeObjectURL(url);
  };

  return (
    <div className="sd-faq-page">
      <div className="sd-faq-page-head">
        <div>
          <h1>FAQ Management</h1>
          <p>Curate and organize public-facing knowledge base articles.</p>
        </div>

        <button className="sd-faq-create-btn" onClick={openCreateModal}>
          <Icon name="add" />
          Create FAQ
        </button>
      </div>

      <div className="sd-faq-layout">
        <aside className="sd-faq-left-panel">
          <Card className="sd-faq-category-card">
            <h2>Categories</h2>

            <button
              className={`sd-faq-category-item ${
                selectedCategory === "ALL" ? "active" : ""
              }`}
              onClick={() => setSelectedCategory("ALL")}
            >
              <div>
                <Icon name="folder" />
                <span>All Articles</span>
              </div>
              <strong>{faqs.length}</strong>
            </button>

            {categoryStats.map((category) => (
              <button
                key={category.value}
                className={`sd-faq-category-item ${
                  selectedCategory === category.value ? "active" : ""
                }`}
                onClick={() => setSelectedCategory(category.value)}
              >
                <div>
                  <Icon name={getCategoryIcon(category.value, categoryOptions)} />
                  <span>{category.label}</span>
                </div>
                <strong>{category.count}</strong>
              </button>
            ))}

            <button
              className="sd-faq-new-category-btn"
              onClick={() => setShowCategoryModal(true)}
            >
              + New Category
            </button>
          </Card>

          <Card className="sd-faq-storage-card">
            <h3>Storage Status</h3>

            <div className="sd-faq-storage-row">
              <span>Public Articles</span>
              <strong>{publicPercent}%</strong>
            </div>

            <div className="sd-faq-storage-track">
              <div style={{ width: `${publicPercent}%` }} />
            </div>

            <p>Next systematic sync scheduled for 02:00 AM UTC.</p>
          </Card>
        </aside>

        <section className="sd-faq-main-panel">
          <div className="sd-faq-toolbar">
            <div className="sd-faq-search-box">
              <Icon name="search" />
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search questions, keywords, or tags..."
              />
            </div>

            <div className="sd-faq-toolbar-actions">
              <span>Sort:</span>

              <select
                className="sd-faq-sort-select"
                value={sortMode}
                onChange={(event) => setSortMode(event.target.value)}
              >
                <option value="RECENT">Recently Added</option>
                <option value="OLDEST">Oldest First</option>
                <option value="AZ">A to Z</option>
                <option value="ZA">Z to A</option>
              </select>

              <div className="sd-faq-filter-wrap">
                <button
                  className={`sd-faq-icon-action ${
                    showFilterPanel || visibilityFilter !== "ALL" ? "active" : ""
                  }`}
                  onClick={() => setShowFilterPanel((prev) => !prev)}
                >
                  <Icon name="filter_list" />
                </button>

                {showFilterPanel && (
                  <div className="sd-faq-filter-panel">
                    <h3>Filter Articles</h3>

                    <label>Visibility</label>
                    <select
                      value={visibilityFilter}
                      onChange={(event) => setVisibilityFilter(event.target.value)}
                    >
                      <option value="ALL">All</option>
                      <option value="PUBLIC">Public Only</option>
                      <option value="INTERNAL">Internal Only</option>
                    </select>

                    <label>Category</label>
                    <select
                      value={selectedCategory}
                      onChange={(event) => setSelectedCategory(event.target.value)}
                    >
                      <option value="ALL">All Categories</option>
                      {categoryOptions.map((category) => (
                        <option key={category.value} value={category.value}>
                          {category.label}
                        </option>
                      ))}
                    </select>

                    <button
                      type="button"
                      onClick={() => {
                        setVisibilityFilter("ALL");
                        setSelectedCategory("ALL");
                        setShowFilterPanel(false);
                      }}
                    >
                      Clear Filters
                    </button>
                  </div>
                )}
              </div>

              <button className="sd-faq-icon-action" onClick={downloadFilteredFAQs}>
                <Icon name="download" />
              </button>
            </div>
          </div>

          <Card className="sd-faq-table-card">
            <table className="sd-faq-table">
              <thead>
                <tr>
                  <th>Question Article</th>
                  <th>Category</th>
                  <th>Visibility</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {paginatedFAQs.map((faq) => {
                  const effectiveCategory = getEffectiveCategoryValue(faq);

                  return (
                    <tr key={faq.id}>
                      <td>
                        <h3>{faq.question}</h3>
                        <p>
                          <Icon name="update" />
                          Updated {formatDate(faq.updated_at || faq.created_at)}
                        </p>
                      </td>

                      <td>
                        <span className="sd-faq-category-pill">
                          {getCategoryLabel(effectiveCategory, categoryOptions)}
                        </span>
                      </td>

                      <td>
                        <div className="sd-faq-visibility-cell">
                          <span>{faq.is_active ? "Public" : "Internal"}</span>

                          <button
                            className={`sd-faq-toggle ${
                              faq.is_active ? "active" : ""
                            }`}
                            onClick={() => toggleVisibility(faq)}
                          >
                            <span />
                          </button>
                        </div>
                      </td>

                      <td>
                        <div className="sd-faq-action-row">
                          <button onClick={() => openEditModal(faq)}>
                            <Icon name="edit" />
                          </button>

                          <button onClick={() => removeFAQ(faq.id)}>
                            <Icon name="delete" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            {filteredFAQs.length === 0 && (
              <div className="sd-faq-empty">No FAQ articles found.</div>
            )}

            <div className="sd-faq-table-footer">
              <span>
                Showing {paginatedFAQs.length} of {filteredFAQs.length} articles
              </span>

              <div>
                <button
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
                >
                  <Icon name="chevron_left" />
                </button>

                {Array.from({ length: totalPages }, (_, index) => index + 1).map(
                  (page) => (
                    <button
                      key={page}
                      className={currentPage === page ? "active" : ""}
                      onClick={() => setCurrentPage(page)}
                    >
                      {page}
                    </button>
                  )
                )}

                <button
                  disabled={currentPage === totalPages}
                  onClick={() =>
                    setCurrentPage((page) => Math.min(totalPages, page + 1))
                  }
                >
                  <Icon name="chevron_right" />
                </button>
              </div>
            </div>
          </Card>
        </section>
      </div>

      {showCategoryModal && (
        <div className="sd-modal-backdrop">
          <div className="sd-faq-small-modal">
            <div className="sd-faq-modal-head">
              <div>
                <h2>Create Category</h2>
                <p>Add a new FAQ category for organizing articles.</p>
              </div>

              <button onClick={() => setShowCategoryModal(false)}>
                <Icon name="close" />
              </button>
            </div>

            <form onSubmit={handleAddCategory}>
              <label className="sd-form-label">Category Name</label>
              <input
                className="sd-input"
                value={newCategoryName}
                onChange={(event) => setNewCategoryName(event.target.value)}
                placeholder="Example: Network Support"
                required
              />

              <div className="sd-faq-modal-footer">
                <button
                  type="button"
                  className="sd-faq-cancel-btn"
                  onClick={() => setShowCategoryModal(false)}
                >
                  Cancel
                </button>

                <button type="submit" className="sd-faq-submit-btn">
                  Create Category
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showFormModal && (
        <div className="sd-modal-backdrop">
          <div className="sd-faq-modal">
            <div className="sd-faq-modal-head">
              <div>
                <h2>{editingId ? "Update FAQ" : "Create FAQ"}</h2>
                <p>Add or update public-facing SmartDesk help content.</p>
              </div>

              <button onClick={closeModal}>
                <Icon name="close" />
              </button>
            </div>

            <form onSubmit={submitFAQ}>
              <div className="sd-form-group">
                <label className="sd-form-label">Question</label>
                <input
                  className="sd-input"
                  name="question"
                  value={form.question}
                  onChange={handleChange}
                  placeholder="How do I reset my organizational password?"
                  required
                />
              </div>

              <div className="sd-form-group">
                <label className="sd-form-label">Answer</label>
                <textarea
                  className="sd-textarea"
                  name="answer"
                  value={form.answer}
                  onChange={handleChange}
                  placeholder="Write the FAQ answer..."
                  rows="5"
                  required
                />
              </div>

              <div className="sd-faq-modal-grid">
                <div>
                  <label className="sd-form-label">Category</label>
                  <select
                    className="sd-select"
                    name="category"
                    value={form.category}
                    onChange={handleChange}
                  >
                    {categoryOptions.map((category) => (
                      <option key={category.value} value={category.value}>
                        {category.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="sd-form-label">Tags</label>
                  <input
                    className="sd-input"
                    name="tags"
                    value={form.tags}
                    onChange={handleChange}
                    placeholder="password, vpn, access"
                  />
                </div>
              </div>

              <div className="sd-faq-modal-footer">
                <button
                  type="button"
                  className="sd-faq-cancel-btn"
                  onClick={closeModal}
                >
                  Cancel
                </button>

                <button type="submit" className="sd-faq-submit-btn">
                  {editingId ? "Update FAQ" : "Create FAQ"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}