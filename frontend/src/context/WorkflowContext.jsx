import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { api } from "../api/client";

const WorkflowContext = createContext(null);
const HISTORY_STORAGE_KEY = "blogy:history:v1";
const PIPELINE_STAGES = [
  "Keyword Clustering",
  "SERP Analysis",
  "Blog Generation",
  "AI Detection",
  "Humanization",
  "SEO Audit",
  "Snippet Optimization",
  "Internal Linking",
];

export function WorkflowProvider({ children }) {
  const [keywordClusters, setKeywordClusters] = useState(null);
  const [serpAnalysis, setSerpAnalysis] = useState(null);
  const [blogResult, setBlogResult] = useState(null);
  const [blogHistory, setBlogHistory] = useState([]);
  const [mongoBlogs, setMongoBlogs] = useState([]);
  const [seoAudit, setSeoAudit] = useState(null);
  const [humanizeResult, setHumanizeResult] = useState(null);

  // alias for compatibility with BlogGenPage naming
  const serpData = serpAnalysis;

  const [loading, setLoading] = useState({});
  const [errors, setErrors] = useState({});
  const [pipelineStepIndex, setPipelineStepIndex] = useState(null);
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const pipelineTimerRef = useRef(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const saved = window.localStorage.getItem(HISTORY_STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) {
          setBlogHistory(parsed);
        }
      }
    } catch (error) {
      console.warn("Failed to load blog history", error);
    }
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      window.localStorage.setItem(
        HISTORY_STORAGE_KEY,
        JSON.stringify(blogHistory),
      );
    } catch (error) {
      console.warn("Failed to persist blog history", error);
    }
  }, [blogHistory]);

  useEffect(() => () => stopPipelineTicker(), []);

  const setLoadingFlag = (key, value) => {
    setLoading((prev) => ({ ...prev, [key]: value }));
  };

  const setErrorFlag = (key, message) => {
    setErrors((prev) => ({ ...prev, [key]: message }));
  };

  const startPipelineTicker = () => {
    stopPipelineTicker();
    setPipelineRunning(true);
    let currentIndex = 0;
    setPipelineStepIndex(0);
    pipelineTimerRef.current = window.setInterval(() => {
      currentIndex = Math.min(currentIndex + 1, PIPELINE_STAGES.length - 1);
      setPipelineStepIndex(currentIndex);
      if (currentIndex === PIPELINE_STAGES.length - 1) {
        stopPipelineTicker();
      }
    }, 1100);
  };

  const stopPipelineTicker = () => {
    if (pipelineTimerRef.current) {
      window.clearInterval(pipelineTimerRef.current);
      pipelineTimerRef.current = null;
    }
    setPipelineRunning(false);
  };

  const addHistoryEntry = (result, keyword) => {
    const entry = {
      id:
        typeof crypto !== "undefined" && crypto.randomUUID
          ? crypto.randomUUID()
          : `${Date.now()}`,
      title: result?.title || "Untitled Blog",
      keyword,
      seoScore: result?.seo_score?.overall_score ?? null,
      createdAt: new Date().toISOString(),
      wordCount: result?.word_count ?? null,
    };
    setBlogHistory((prev) => [entry, ...prev].slice(0, 25));
  };

  const runKeywordCluster = async (payload) => {
    setLoadingFlag("keywordCluster", true);
    setErrorFlag("keywordCluster", null);
    try {
      const result = await api.keywords.cluster(payload);
      setKeywordClusters(result);
      return result;
    } catch (error) {
      setErrorFlag(
        "keywordCluster",
        error.message || "Unable to cluster keywords",
      );
      throw error;
    } finally {
      setLoadingFlag("keywordCluster", false);
    }
  };

  const runSerpAnalysis = async (payload) => {
    setLoadingFlag("serpAnalysis", true);
    setErrorFlag("serpAnalysis", null);
    try {
      const result = await api.serp.analyze(payload);
      setSerpAnalysis(result);
      return result;
    } catch (error) {
      setErrorFlag("serpAnalysis", error.message || "SERP analysis failed");
      throw error;
    } finally {
      setLoadingFlag("serpAnalysis", false);
    }
  };

  const generateBlog = async (payload) => {
    setLoadingFlag("blogGeneration", true);
    setErrorFlag("blogGeneration", null);
    startPipelineTicker();
    try {
      const result = await api.blog.generate(payload);
      setBlogResult(result);
      if (result.keyword_clusters) {
        setKeywordClusters(result.keyword_clusters);
      }
      if (result.serp_analysis) {
        setSerpAnalysis(result.serp_analysis);
      }
      addHistoryEntry(result, payload.keyword);
      setPipelineStepIndex(PIPELINE_STAGES.length - 1);
      stopPipelineTicker();
      // Refresh mongo blog list after generation
      api.blog
        .list()
        .then(setMongoBlogs)
        .catch(() => {});
      return result;
    } catch (error) {
      setErrorFlag("blogGeneration", error.message || "Blog generation failed");
      throw error;
    } finally {
      stopPipelineTicker();
      setLoadingFlag("blogGeneration", false);
    }
  };

  const fetchBlogHistory = async ({ limit = 50, status } = {}) => {
    setLoadingFlag("blogHistory", true);
    setErrorFlag("blogHistory", null);
    try {
      const results = await api.blog.list({ limit, status });
      setMongoBlogs(results);
      return results;
    } catch (error) {
      // Non-fatal — backend might not be running
      setErrorFlag(
        "blogHistory",
        error.message || "Failed to load blog history",
      );
      return [];
    } finally {
      setLoadingFlag("blogHistory", false);
    }
  };

  const deleteBlog = async (blogId) => {
    try {
      await api.blog.delete(blogId);
      setMongoBlogs((prev) => prev.filter((b) => b.id !== blogId));
    } catch (error) {
      throw new Error(error.message || "Failed to delete blog");
    }
  };

  const updateBlogStatus = async (blogId, status) => {
    try {
      await api.blog.updateStatus(blogId, status);
      setMongoBlogs((prev) =>
        prev.map((b) => (b.id === blogId ? { ...b, status } : b)),
      );
    } catch (error) {
      throw new Error(error.message || "Failed to update blog status");
    }
  };

  const runHumanize = async (payload) => {
    setLoadingFlag("humanize", true);
    setErrorFlag("humanize", null);
    try {
      const result = await api.humanize.run(payload);
      setHumanizeResult(result);
      return result;
    } catch (error) {
      setErrorFlag("humanize", error.message || "Humanization failed");
      throw error;
    } finally {
      setLoadingFlag("humanize", false);
    }
  };

  const runSEOAudit = async (payload) => {
    setLoadingFlag("seoAudit", true);
    setErrorFlag("seoAudit", null);
    try {
      const result = await api.seo.analyze(payload);
      setSeoAudit(result);
      return result;
    } catch (error) {
      setErrorFlag("seoAudit", error.message || "SEO audit failed");
      throw error;
    } finally {
      setLoadingFlag("seoAudit", false);
    }
  };

  const value = useMemo(
    () => ({
      keywordClusters,
      serpAnalysis,
      serpData,
      blogResult,
      blogHistory,
      mongoBlogs,
      seoAudit,
      humanizeResult,
      pipelineStages: PIPELINE_STAGES,
      pipelineStepIndex,
      pipelineRunning,
      loading,
      errors,
      actions: {
        runKeywordCluster,
        runSerpAnalysis,
        generateBlog,
        runHumanize,
        runSEOAudit,
        fetchBlogHistory,
        deleteBlog,
        updateBlogStatus,
      },
    }),
    [
      keywordClusters,
      serpAnalysis,
      blogResult,
      blogHistory,
      mongoBlogs,
      seoAudit,
      humanizeResult,
      pipelineStepIndex,
      pipelineRunning,
      loading,
      errors,
    ],
  );

  return (
    <WorkflowContext.Provider value={value}>
      {children}
    </WorkflowContext.Provider>
  );
}

export function useWorkflow() {
  const context = useContext(WorkflowContext);
  if (!context) {
    throw new Error("useWorkflow must be used within a WorkflowProvider");
  }
  return context;
}
