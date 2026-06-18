import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LogOut, Globe, Mail, ShieldCheck, AlertCircle, 
  CheckCircle2, RefreshCw, ArrowLeft, ArrowRight, ExternalLink, 
  Lock, ChevronDown, ChevronUp, FileText, Settings, Send,
  Layers, Copy, Check, Terminal, FileJson, Info, Eye, Search, Filter
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5001';

export default function SubmitWebsite() {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  // Core Form states
  const [url, setUrl] = useState('');
  const [siteName, setSiteName] = useState('');
  const [description, setDescription] = useState('');
  const [sitemapUrl, setSitemapUrl] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [submitterName, setSubmitterName] = useState('');
  const [tenWordsTwitterHandle, setTenWordsTwitterHandle] = useState('');
  const [tenWordsCategory, setTenWordsCategory] = useState('Website');
  const [tenWordsNewsletter, setTenWordsNewsletter] = useState('No thanks');
  const [futureToolsCategory, setFutureToolsCategory] = useState('Productivity');
  const [futureToolsPricing, setFutureToolsPricing] = useState('Free');
  const [futureToolsNewsletterOptIn, setFutureToolsNewsletterOptIn] = useState(false);
  const [alternativeCategory, setAlternativeCategory] = useState('software/web/tools');
  const [alternativeFullDescription, setAlternativeFullDescription] = useState('');
  const [alternativePricingUrl, setAlternativePricingUrl] = useState('');
  const [alternativeType, setAlternativeType] = useState('online');
  const [alternativeMonetization, setAlternativeMonetization] = useState('free');
  const [alternativeStatus, setAlternativeStatus] = useState('live');
  const [alternativePlatforms, setAlternativePlatforms] = useState('');
  const [alternativeFeatures, setAlternativeFeatures] = useState('');
  const [alternativeSocialLinks, setAlternativeSocialLinks] = useState('');
  const [alternativeSocialLinkUrl, setAlternativeSocialLinkUrl] = useState('');
  const [alternativeSocialLinkType, setAlternativeSocialLinkType] = useState('twitter');
  const [alternativePricingName, setAlternativePricingName] = useState('');
  const [alternativePricingCost, setAlternativePricingCost] = useState('');
  const [alternativeSynonyms, setAlternativeSynonyms] = useState('');
  const [alternativeTestSoftwareName, setAlternativeTestSoftwareName] = useState('');
  const [alternativeTestHomepageUrl, setAlternativeTestHomepageUrl] = useState('');
  const [alternativeTestShortDescription, setAlternativeTestShortDescription] = useState('');
  const [alternativeTestFullDescription, setAlternativeTestFullDescription] = useState('');
  const [alternativeIconPath, setAlternativeIconPath] = useState('/Users/nolanpham/Documents/SEO_Tools/backend/seo-audit-worker/.playwright/alternative-icon.png');
  const [alternativeTestCategory, setAlternativeTestCategory] = useState('software/web/tools');
  const [alternativeTestPricingUrl, setAlternativeTestPricingUrl] = useState('');
  const [alternativeTestType, setAlternativeTestType] = useState('online');
  const [alternativeTestMonetization, setAlternativeTestMonetization] = useState('free');
  const [alternativeTestStatus, setAlternativeTestStatus] = useState('live');
  const [alternativeTestPlatforms, setAlternativeTestPlatforms] = useState('');
  const [alternativeTestFeatures, setAlternativeTestFeatures] = useState('');
  const [alternativeTestSocialLinkType, setAlternativeTestSocialLinkType] = useState('twitter');
  const [alternativeTestSocialLinkUrl, setAlternativeTestSocialLinkUrl] = useState('');
  const [alternativeTestPricingName, setAlternativeTestPricingName] = useState('');
  const [alternativeTestPricingCost, setAlternativeTestPricingCost] = useState('');
  const [alternativeTestSynonyms, setAlternativeTestSynonyms] = useState('');
  const [awesomeIndieTagline, setAwesomeIndieTagline] = useState('');
  const [awesomeIndieCategories, setAwesomeIndieCategories] = useState('AI Tools, Productivity');
  const [awesomeIndieDescription, setAwesomeIndieDescription] = useState('');
  const [awesomeIndieSocialLinks, setAwesomeIndieSocialLinks] = useState('');
  const [awesomeIndieYouTubeVideoUrl, setAwesomeIndieYouTubeVideoUrl] = useState('');
  
  // Dashboard platform selection & filtering
  const [platforms, setPlatforms] = useState([]);
  const [isLoadingPlatforms, setIsLoadingPlatforms] = useState(true);
  const [selectedPlatformId, setSelectedPlatformId] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [methodFilter, setMethodFilter] = useState('ALL'); // 'ALL', 'API', 'AUTOMATION'
  
  // Platform settings
  const [activeSettingsPlatformId, setActiveSettingsPlatformId] = useState(null);
  const [connectSuccess, setConnectSuccess] = useState('');
  const [connectError, setConnectError] = useState('');
  const [isConnectingPlatform, setIsConnectingPlatform] = useState(false);
  const [sessionFile, setSessionFile] = useState(null);

  // Job Submission States
  const [isSubmittingJob, setIsSubmittingJob] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [submitSuccess, setSubmitSuccess] = useState('');
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  // Jobs History & Details States
  const [jobs, setJobs] = useState([]);
  const [isLoadingJobs, setIsLoadingJobs] = useState(true);
  const [jobsError, setJobsError] = useState('');
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [jobDetails, setJobDetails] = useState(null);
  const [isLoadingJobDetails, setIsLoadingJobDetails] = useState(false);  
  const [jobDetailsError, setJobDetailsError] = useState('');
  const [isRefreshingHistory, setIsRefreshingHistory] = useState(false);

  // UI state
  const [expandedDetailId, setExpandedDetailId] = useState(null);
  const [copiedDataId, setCopiedDataId] = useState(null);

  // Polling ref
  const pollingIntervalRef = useRef(null);

  // Fetch active platforms
  const fetchPlatforms = async () => {
    try {
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/submit/platforms`, {
        headers: {
          'Authorization': `Bearer ${idToken}`
        }
      });
      if (!response.ok) throw new Error('Không thể lấy danh sách platforms.');
      const data = await response.json();
      setPlatforms(data);
      
      const preferredCodes = ['newaiforyou', 'new_ai_for_you', 'awesome_indie', 'awesomeindie', 'kyi_ai', 'kyi', '10words', 'baitools', 'alternative', 'futuretools', 'productburst', 'stackshare'];
      const preferredPlatform = preferredCodes
        .map((code) => data.find((platform) => platform.code?.toLowerCase() === code))
        .find(Boolean);

      // Auto-select the preferred platform by default
      if (preferredPlatform) {
        setSelectedPlatformId(preferredPlatform.id);
      } else if (data.length > 0) {
        setSelectedPlatformId(data[0].id);
      }
    } catch (err) {
      console.error(err);
      setSubmitError('Lỗi tải danh sách SEO platforms.');
    } finally {
      setIsLoadingPlatforms(false);
    }
  };

  // Fetch jobs history
  const fetchJobs = async (silent = false) => {
    if (!silent) setIsLoadingJobs(true);
    else setIsRefreshingHistory(true);
    try {
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/submit/history`, {
        headers: {
          'Authorization': `Bearer ${idToken}`
        }
      });
      if (!response.ok) throw new Error('Không thể tải lịch sử submit.');
      const data = await response.json();
      setJobs(data);
      setJobsError('');
    } catch (err) {
      console.error(err);
      setJobsError('Đã xảy ra lỗi khi tải danh sách lịch sử.');
    } finally {
      setIsLoadingJobs(false);
      setIsRefreshingHistory(false);
    }
  };

  // Fetch single job details (progress)
  const fetchJobDetails = async (id, silent = false) => {
    if (!silent) setIsLoadingJobDetails(true);
    try {
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/submit/jobs/${id}`, {
        headers: {
          'Authorization': `Bearer ${idToken}`
        }
      });
      if (!response.ok) throw new Error('Không thể tải chi tiết tiến trình.');
      const data = await response.json();
      setJobDetails(data);
      setJobDetailsError('');
    } catch (err) {
      console.error(err);
      setJobDetailsError('Lỗi khi tải chi tiết tiến trình submit.');
    } finally {
      if (!silent) setIsLoadingJobDetails(false);
    }
  };

  // Import locally generated StackShare session
  const handleImportPlatformSession = async (platformId) => {
    setConnectError('');
    setConnectSuccess('');
    setIsConnectingPlatform(true);

    if (!sessionFile) {
      setConnectError('Vui lòng chọn file stackshare_storage_state.json trước khi import.');
      setIsConnectingPlatform(false);
      return;
    }

    try {
      const credentialData = await sessionFile.text();
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/submit/credentials`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${idToken}`
        },
        body: JSON.stringify({
          platformId,
          credentialData
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.Message || 'Không thể import session.');
      }

      setConnectSuccess('Đã import session thành công. Docker sẽ dùng storage_state này cho Submit.');
      setSessionFile(null);

      setTimeout(() => {
        setConnectSuccess('');
        setActiveSettingsPlatformId(null);
      }, 2000);
    } catch (err) {
      setConnectError(err.message);
    } finally {
      setIsConnectingPlatform(false);
    }
  };

  const fillAlternativeTestSample = () => {
    setSiteName(alternativeTestSoftwareName);
    setUrl(alternativeTestHomepageUrl);
    setDescription(alternativeTestShortDescription);
    setAlternativeFullDescription(alternativeTestFullDescription);
    setAlternativeCategory(alternativeTestCategory);
    setAlternativePricingUrl(alternativeTestPricingUrl);
    setAlternativeType(alternativeTestType);
    setAlternativeMonetization(alternativeTestMonetization);
    setAlternativeStatus(alternativeTestStatus);
    setAlternativePlatforms(alternativeTestPlatforms);
    setAlternativeFeatures(alternativeTestFeatures);
    setAlternativeSocialLinkType(alternativeTestSocialLinkType);
    setAlternativeSocialLinks(alternativeTestSocialLinkUrl);
    setAlternativePricingName(alternativeTestPricingName);
    setAlternativePricingCost(alternativeTestPricingCost);
    setAlternativeSynonyms(alternativeTestSynonyms);
    setAlternativeIconPath('');
  };

  const fillAlternativeFullSample = () => {
    setAlternativeTestSoftwareName('Langflow');
    setAlternativeTestHomepageUrl('https://www.langflow.org');
    setAlternativeTestShortDescription(
      'Build and run LLM workflows with a visual builder for AI apps and automation. It supports reusable components, debugging, and team collaboration for production use.'
    );
    setAlternativeTestFullDescription(
      'Langflow is a low-code platform for designing, testing, and deploying LLM workflows with reusable components, integrations, and API support. It helps teams prototype faster, connect multiple models and tools, and move from experiments to production with a more structured workflow builder.'
    );
    setAlternativeTestCategory('software/web/tools');
    setAlternativeTestPricingUrl('https://www.langflow.org/pricing');
    setAlternativeTestType('online');
    setAlternativeTestMonetization('free');
    setAlternativeTestStatus('live');
    setAlternativeTestPlatforms('OpenAI, LangChain, Zapier');
    setAlternativeTestFeatures('visual builder, LLM workflows, reusable components, automation, API');
    setAlternativeTestSocialLinkType('twitter');
    setAlternativeTestSocialLinkUrl('https://x.com/langflow');
    setAlternativeTestPricingName('Pro');
    setAlternativeTestPricingCost('29');
    setAlternativeTestSynonyms('Lang Flow, Langflow AI');
    setAlternativeIconPath('/Users/nolanpham/Documents/SEO_Tools/backend/seo-audit-worker/.playwright/alternative-icon.png');

    setSiteName('Langflow');
    setUrl('https://www.langflow.org');
    setDescription(
      'Build and run LLM workflows with a visual builder for AI apps and automation. It supports reusable components, debugging, and team collaboration for production use.'
    );
    setAlternativeFullDescription(
      'Langflow is a low-code platform for designing, testing, and deploying LLM workflows with reusable components, integrations, and API support. It helps teams prototype faster, connect multiple models and tools, and move from experiments to production with a more structured workflow builder.'
    );
    setAlternativeCategory('software/web/tools');
    setAlternativePricingUrl('https://www.langflow.org/pricing');
    setAlternativeType('online');
    setAlternativeMonetization('free');
    setAlternativeStatus('live');
    setAlternativePlatforms('OpenAI, LangChain, Zapier');
    setAlternativeFeatures('visual builder, LLM workflows, reusable components, automation, API');
    setAlternativeSocialLinkType('twitter');
    setAlternativeSocialLinks('https://x.com/langflow');
    setAlternativePricingName('Pro');
    setAlternativePricingCost('29');
    setAlternativeSynonyms('Lang Flow, Langflow AI');
    setAlternativeIconPath('/Users/nolanpham/Documents/SEO_Tools/backend/seo-audit-worker/.playwright/alternative-icon.png');
  };

  const fillNewAIForYouDemoSample = () => {
    setSiteName('Langflow');
    setUrl('https://www.langflow.org');
  };

  const fillAwesomeIndieDemoSample = () => {
    setSiteName('Langflow');
    setUrl('https://www.langflow.org');
    setAwesomeIndieTagline('Build and ship LLM workflows visually');
    setAwesomeIndieCategories('AI Tools, Productivity');
    setAwesomeIndieDescription(
      'Langflow is a low-code platform for designing, testing, and deploying LLM workflows with reusable components, integrations, and API support.'
    );
    setAwesomeIndieSocialLinks('https://x.com/langflow, https://github.com/langflow-ai/langflow');
    setAwesomeIndieYouTubeVideoUrl('https://www.youtube.com/watch?v=dQw4w9WgXcQ');
    setDescription(
      'Langflow is a low-code platform for designing, testing, and deploying LLM workflows with reusable components, integrations, and API support.'
    );
  };

  const fillTenWordsQuickSample = () => {
    setSiteName('SEO TOOLS');
    setUrl('https://example.com');
    setDescription('A modern SEO toolkit');
    setTenWordsTwitterHandle('@seotools');
    setTenWordsCategory('Website');
    setTenWordsNewsletter('No thanks');
  };

  const fillTenWordsDemoSample = () => {
    setSiteName('Langflow');
    setUrl('https://www.langflow.org');
    setDescription('Build and run LLM');
    setTenWordsTwitterHandle('@langflow');
    setTenWordsCategory('SaaS');
    setTenWordsNewsletter('Weekly');
  };

  // Submit website job
  const handleFormSubmit = (e) => {
    e.preventDefault();
    setSubmitError('');
    setSubmitSuccess('');

    if (!url) return setSubmitError('Vui lòng nhập URL website cần submit.');
    if (!selectedPlatformId) return setSubmitError('Vui lòng chọn một platform.');

    try {
      new URL(url);
    } catch (_) {
      return setSubmitError('Định dạng URL không hợp lệ (ví dụ: https://example.com).');
    }

    const currentPlatform = platforms.find(p => p.id === selectedPlatformId);
    const isNewAIForYou = currentPlatform?.code?.toLowerCase() === 'newaiforyou' || currentPlatform?.code?.toLowerCase() === 'new_ai_for_you' || currentPlatform?.code?.toLowerCase() === 'new-ai-for-you';
    const isAwesomeIndie = currentPlatform?.code?.toLowerCase() === 'awesome_indie' || currentPlatform?.code?.toLowerCase() === 'awesomeindie' || currentPlatform?.code?.toLowerCase() === 'awesome-indie';
    const isTenWords = currentPlatform?.code?.toLowerCase() === '10words';
    const isBAI = currentPlatform?.code?.toLowerCase() === 'baitools';
    const isASR = currentPlatform?.code?.toLowerCase() === 'asr' || currentPlatform?.code?.toLowerCase() === 'active_search_results';
    const isFutureTools = currentPlatform?.code?.toLowerCase() === 'futuretools';
    const isAlternative = currentPlatform?.code?.toLowerCase() === 'alternative';

    if (isNewAIForYou) {
      if (!siteName) return setSubmitError('Vui lòng nhập Tool name cho New AI For You.');
      if (!url) return setSubmitError('Vui lòng nhập URL cho New AI For You.');
    }

    if (isAwesomeIndie) {
      if (!siteName) return setSubmitError('Vui lòng nhập Product name cho Awesome Indie.');
      if (!url) return setSubmitError('Vui lòng nhập URL cho Awesome Indie.');
      if (!awesomeIndieTagline) return setSubmitError('Vui lòng nhập Tagline cho Awesome Indie.');
      if (!awesomeIndieCategories) return setSubmitError('Vui lòng nhập Categories cho Awesome Indie.');
      if (!awesomeIndieDescription) return setSubmitError('Vui lòng nhập Description cho Awesome Indie.');
    }

    if (isTenWords) {
      if (!siteName) return setSubmitError('Vui lòng nhập Project Name cho 10words.');
      if (!url) return setSubmitError('Vui lòng nhập Project URL cho 10words.');
      if (!description) return setSubmitError('Vui lòng nhập Description cho 10words.');
      if (!tenWordsCategory) return setSubmitError('Vui lòng chọn Category cho 10words.');
    }

    if (isBAI) {
      if (!siteName) return setSubmitError('Vui lòng nhập AI Tool Name cho BAI.tools.');
      if (!url) return setSubmitError('Vui lòng nhập Website URL cho BAI.tools.');
    }
    
    if (isASR && !contactEmail) {
      return setSubmitError('Vui lòng nhập Contact Email cho Active Search Results.');
    }

    if (isFutureTools) {
      if (!submitterName) return setSubmitError('Vui lòng nhập Your Name cho Future Tools.');
      if (!siteName) return setSubmitError('Vui lòng nhập Tool Name cho Future Tools.');
      if (!description) return setSubmitError('Vui lòng nhập Short Description cho Future Tools.');
      if (!contactEmail) return setSubmitError('Vui lòng nhập Your Email cho Future Tools.');
    }

    if (isAlternative) {
      if (!siteName) return setSubmitError('Vui lòng nhập Software Name cho Alternative.');
      if (!url) return setSubmitError('Vui lòng nhập Homepage URL cho Alternative.');
      if (!description) return setSubmitError('Vui lòng nhập Short Description cho Alternative.');
      if (!alternativeCategory) return setSubmitError('Vui lòng chọn Category cho Alternative.');
      if (!alternativeIconPath) return setSubmitError('Vui lòng nhập Icon Path cho Alternative.');
    }

    // Open confirmation dialog
    setShowConfirmDialog(true);
  };

  const executeSubmitJob = async () => {
    setShowConfirmDialog(false);
    setIsSubmittingJob(true);
    setSubmitError('');
    
    try {
      const currentPlatform = platforms.find(p => p.id === selectedPlatformId);
      const isNewAIForYou = currentPlatform?.code?.toLowerCase() === 'newaiforyou' || currentPlatform?.code?.toLowerCase() === 'new_ai_for_you' || currentPlatform?.code?.toLowerCase() === 'new-ai-for-you';
      const isAwesomeIndie = currentPlatform?.code?.toLowerCase() === 'awesome_indie' || currentPlatform?.code?.toLowerCase() === 'awesomeindie' || currentPlatform?.code?.toLowerCase() === 'awesome-indie';
      const isTenWords = currentPlatform?.code?.toLowerCase() === '10words';
      const isBAI = currentPlatform?.code?.toLowerCase() === 'baitools';
      const isAlternative = currentPlatform?.code?.toLowerCase() === 'alternative';
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/submit/jobs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${idToken}`
        },
        body: JSON.stringify({
          websiteUrl: url,
          platformIds: [selectedPlatformId],
          siteName: siteName || undefined,
          description: isAwesomeIndie ? awesomeIndieDescription || undefined : description || undefined,
          sitemapUrl: sitemapUrl || undefined,
          contactEmail: contactEmail || undefined,
          yourName: submitterName || undefined,
          tagline: isAwesomeIndie ? awesomeIndieTagline || undefined : undefined,
          categories: isAwesomeIndie ? awesomeIndieCategories || undefined : isTenWords ? tenWordsCategory || undefined : isAlternative ? alternativeCategory || undefined : undefined,
          socialLinks: isAwesomeIndie ? awesomeIndieSocialLinks || undefined : isAlternative ? alternativeSocialLinks || undefined : undefined,
          YouTubeVideoUrl: isAwesomeIndie ? awesomeIndieYouTubeVideoUrl || undefined : undefined,
          category: isTenWords
            ? tenWordsCategory || undefined
            : isAlternative
              ? alternativeCategory || undefined
              : isBAI
                ? 'Website'
                : isAwesomeIndie
                  ? undefined
                  : futureToolsCategory || undefined,
          tenWordsCategory: isTenWords ? tenWordsCategory || undefined : undefined,
          BAIToolsUseApi: isBAI ? true : undefined,
          BAIToolsPlanIndex: isBAI ? 0 : undefined,
          BAIToolsLocale: isBAI ? 'en' : undefined,
          KyiAiDebugHeadful: isActivePlatformKyi ? true : undefined,
          AwesomeIndieDebugHeadful: isAwesomeIndie ? true : undefined,
          NewAIForYouDebugHeadful: isNewAIForYou ? true : undefined,
          iconPath: isAlternative ? alternativeIconPath || undefined : undefined,
          fullDescription: isAlternative ? alternativeFullDescription || undefined : undefined,
          homepageUrl: isAlternative ? url || undefined : undefined,
          pricingUrl: isAlternative ? alternativePricingUrl || undefined : undefined,
          type: isAlternative ? alternativeType || undefined : undefined,
          monetization: isAlternative ? alternativeMonetization || undefined : undefined,
          status: isAlternative ? alternativeStatus || undefined : undefined,
          platforms: isAlternative ? alternativePlatforms || undefined : undefined,
          features: isAlternative ? alternativeFeatures || undefined : undefined,
          socialLinks: isAlternative ? alternativeSocialLinks || undefined : undefined,
          alternativeSocialLinkType: isAlternative ? alternativeSocialLinkType || undefined : undefined,
          alternativePricingName: isAlternative ? alternativePricingName || undefined : undefined,
          alternativePricingCost: isAlternative ? alternativePricingCost || undefined : undefined,
          synonyms: isAlternative ? alternativeSynonyms || undefined : undefined,
          twitterHandle: isTenWords ? tenWordsTwitterHandle || undefined : undefined,
          tenWordsNewsletter: isTenWords ? tenWordsNewsletter || undefined : undefined,
          pricing: futureToolsPricing || undefined,
          newsletterOptIn: futureToolsNewsletterOptIn ? 'true' : undefined
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.Message || 'Gửi yêu cầu submit thất bại.');
      }
      
      const data = await response.json();
      setSubmitSuccess('Gửi yêu cầu thành công! Đang tiến hành submit bất đồng bộ...');
      
      // Reset form URL, keep contactEmail for convenience
      setUrl('');
      
      fetchJobs(true);
      if (data.jobId) { 
        setSelectedJobId(data.jobId);
      }
    } catch (err) {
      setSubmitError(err.message);
    } finally {
      setIsSubmittingJob(false);
    }
  };

  // Initial Load
  useEffect(() => {
    fetchPlatforms();
    fetchJobs();
  }, []);

  useEffect(() => {
    const fallbackName = currentUser?.displayName || currentUser?.email?.split('@')?.[0] || '';
    if (!submitterName && fallbackName) {
      setSubmitterName(fallbackName);
    }
  }, [currentUser, submitterName]);

  // Poll status of running submit jobs
  useEffect(() => {
    const hasRunningJobs = jobs.some(j => j.status === 'Pending' || j.status === 'Running');
    const isCurrentJobRunning = jobDetails && (jobDetails.status === 'Pending' || jobDetails.status === 'Running');

    if (hasRunningJobs || isCurrentJobRunning) {
      pollingIntervalRef.current = setInterval(() => {
        fetchJobs(true);
        if (selectedJobId) {
          fetchJobDetails(selectedJobId, true);
        }
      }, 3000);
    } else {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    }

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, [jobs, selectedJobId, jobDetails]);

  // Fetch job details on selection
  useEffect(() => {
    if (selectedJobId) {
      fetchJobDetails(selectedJobId);
    } else {
      setJobDetails(null);
    }
    setExpandedDetailId(null);
  }, [selectedJobId]);

  async function handleLogout() {
    try {
      await logout();
      navigate('/login');
    } catch (err) {
      console.error(err);
    }
  }

  const getStatusLabel = (status) => {
    switch (status) {
      case 'Pending': return 'Chờ hàng đợi';
      case 'Running': return 'Đang chạy';
      case 'Success': return 'Thành công';
      case 'Failed': return 'Thất bại';
      case 'Completed': return 'Hoàn thành';
      case 'RequiresManualAction': return 'Cần tương tác';
      default: return status;
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'Pending': return 'pending';
      case 'Running': return 'processing';
      case 'Success':
      case 'Completed': return 'completed';
      case 'Failed': return 'failed';
      case 'RequiresManualAction': return 'warning';
      default: return 'failed';
    }
  };

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedDataId(id);
    setTimeout(() => setCopiedDataId(null), 2000);
  };

  const handleAddAlternativeSocialLink = () => {
    const nextUrl = alternativeSocialLinkUrl.trim();
    if (!nextUrl) return;
    setAlternativeSocialLinks((current) => (current ? `${current}, ${nextUrl}` : nextUrl));
    setAlternativeSocialLinkUrl('');
  };

  // Filtered platforms logic
  const filteredPlatforms = platforms.filter(platform => {
    const matchesSearch = platform.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          platform.code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesMethod = methodFilter === 'ALL' ||
                          (methodFilter === 'API' && platform.submitMethod === 'API') ||
                          (methodFilter === 'AUTOMATION' && platform.submitMethod !== 'API');
    return matchesSearch && matchesMethod;
  });

  const activePlatform = platforms.find(p => p.id === selectedPlatformId);
  const isActivePlatformNewAIForYou = activePlatform?.code?.toLowerCase() === 'newaiforyou' || activePlatform?.code?.toLowerCase() === 'new_ai_for_you' || activePlatform?.code?.toLowerCase() === 'new-ai-for-you';
  const isActivePlatformAwesomeIndie = activePlatform?.code?.toLowerCase() === 'awesome_indie' || activePlatform?.code?.toLowerCase() === 'awesomeindie' || activePlatform?.code?.toLowerCase() === 'awesome-indie';
  const isActivePlatformKyi = activePlatform?.code?.toLowerCase() === 'kyi' || activePlatform?.code?.toLowerCase() === 'kyi_ai' || activePlatform?.code?.toLowerCase() === 'kyiai';
  const isActivePlatformTenWords = activePlatform?.code?.toLowerCase() === '10words';
  const isActivePlatformBAI = activePlatform?.code?.toLowerCase() === 'baitools';
  const isActivePlatformStackShare = activePlatform?.code?.toLowerCase() === 'stackshare';
  const isActivePlatformASR = activePlatform?.code?.toLowerCase() === 'asr' || activePlatform?.code?.toLowerCase() === 'active_search_results';
  const isActivePlatformFutureTools = activePlatform?.code?.toLowerCase() === 'futuretools';
  const isActivePlatformAlternative = activePlatform?.code?.toLowerCase() === 'alternative';
  const tenWordsPreviewData = isActivePlatformTenWords ? {
    project_name: siteName,
    project_url: url,
    description,
    twitter_handle: tenWordsTwitterHandle,
    category: tenWordsCategory,
    newsletter: tenWordsNewsletter,
  } : null;

  // Platform specific static metadata for visual cards (like tags and short descriptions in the reference image)
  const getPlatformMetadata = (code) => {
    const normalized = code?.toLowerCase();
    if (normalized === 'kyi' || normalized === 'kyi_ai' || normalized === 'kyiai') {
      return {
        tags: ['AI Tools', 'No Login', 'Public Form'],
        description: 'Mở trang submit Kyi AI, điền website name, URL và email rồi bấm Submit để chờ pop-up success.',
        speed: '30-60 giây',
        cost: 'Free',
        typeLabel: 'AUTOMATION'
      };
    }
    if (normalized === 'newaiforyou' || normalized === 'new_ai_for_you' || normalized === 'new-ai-for-you') {
      return {
        tags: ['AI Tools', 'Google OAuth', 'Modal Success'],
        description: 'Đăng nhập Google, mở trang submit New AI For You, điền tool name và URL rồi chờ modal success quay về home.',
        speed: '1-2 phút',
        cost: 'Free',
        typeLabel: 'AUTOMATION'
      };
    }
    if (normalized === 'awesome_indie' || normalized === 'awesomeindie' || normalized === 'awesome-indie') {
      return {
        tags: ['AI Tools', 'Google OAuth', 'Product Submission'],
        description: 'Đăng nhập Google, bấm AddProduct để vào trang submit và điền product name, URL, tagline, categories, description, social links và video.',
        speed: '2-4 phút',
        cost: 'Free',
        typeLabel: 'AUTOMATION'
      };
    }
    if (normalized === 'stackshare') {
      return {
        tags: ['Developer Tools', 'Automation', 'Social'],
        description: 'Tự động mở trình duyệt chạy ngầm để điền form, crawl dữ liệu website và submit công cụ lập trình của bạn.',
        speed: '2-3 phút',
        cost: 'Free',
        typeLabel: 'AUTOMATION'
      };
    }
    if (normalized === '10words') {
      return {
        tags: ['AI Tools', 'OAuth', 'Automation'],
        description: 'Mở portal 10words, điền form submit project bằng browser thật và lưu đúng session nếu cần xác thực.',
        speed: '1-2 phút',
        cost: 'Free',
        typeLabel: 'AUTOMATION'
      };
    }
    if (normalized === 'baitools') {
      return {
        tags: ['AI Tools', 'OAuth', 'Automation'],
        description: 'Mở form submit của BAI.tools, tự động điền dữ liệu dự án AI và chuyển tới trang finish sau submit.',
        speed: '1-2 phút',
        cost: 'Free',
        typeLabel: 'AUTOMATION'
      };
    }
    if (normalized === 'futuretools') {
      return {
        tags: ['AI Tools', 'No Login', 'Automation'],
        description: 'Mở trang submit của Future Tools, tự động điền form giới thiệu công cụ AI và bấm submit bằng browser thật.',
        speed: '1-2 phút',
        cost: 'Free',
        typeLabel: 'AUTOMATION'
      };
    }
    if (normalized === 'alternative') {
      return {
        tags: ['Software', 'Login Required', 'Automation'],
        description: 'Mở form Software Submission của Alternative, chờ đăng nhập thủ công nếu cần rồi tự động điền và gửi form.',
        speed: '2-4 phút',
        cost: 'Free',
        typeLabel: 'AUTOMATION'
      };
    }
    if (normalized === 'asr' || normalized === 'active_search_results') {
      return {
        tags: ['SEO Directory', 'HTTP Direct', 'Instant'],
        description: 'Gửi HTTP POST request trực tiếp lên danh bạ Active Search Results để index website nhanh chóng và miễn phí.',
        speed: 'Tức thì',
        cost: 'Free',
        typeLabel: 'API DIRECT'
      };
    }
    return {
      tags: ['SEO Platform', 'Indexing'],
      description: 'Nền tảng hỗ trợ Submit website giúp tối ưu chỉ mục công cụ tìm kiếm và danh bạ internet.',
      speed: 'Tùy biến',
      cost: 'Free',
      typeLabel: 'SUBMIT'
    };
  };

  return (
    <div className="dashboard-grid">
      {/* LEFT COLUMN: Profile, Navigation & Indexing History */}
      <div className="dashboard-panel">
        {/* Profile Card */}
        <div className="sidebar-profile">
          <div className="sidebar-avatar-placeholder">
            {currentUser?.email ? currentUser.email.substring(0, 2).toUpperCase() : 'US'}
          </div>
          <div className="sidebar-info">
            <div className="sidebar-name">{currentUser?.displayName || 'SEO Manager'}</div>
            <div className="sidebar-email">{currentUser?.email}</div>
          </div>
          <button 
            onClick={handleLogout} 
            className="refresh-btn" 
            title="Đăng xuất"
            style={{ color: 'hsl(var(--accent-error))' }}
          >
            <LogOut size={18} />
          </button>
        </div>

        {/* Feature Navigation Toggle */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <button 
            onClick={() => navigate('/')} 
            className="btn btn-outline" 
            style={{ flex: 1, padding: '0.5rem', fontSize: '0.8rem', display: 'flex', gap: '4px', justifyContent: 'center', alignItems: 'center' }}
          >
            <ArrowLeft size={14} /> Crawl & Audit SEO
          </button>
          <button 
            className="btn btn-primary" 
            style={{ flex: 1, padding: '0.5rem', fontSize: '0.8rem', cursor: 'default' }}
            disabled
          >
            Submit SEO Platforms
          </button>
        </div>

        {/* JOBS HISTORY LIST VIEW */}
        <div>
          <div className="audit-list-header">
            <h2 className="audit-list-title" style={{ fontSize: '1.05rem', fontWeight: 600 }}>Lịch Sử Gửi Chỉ Mục</h2>
            <button 
              onClick={() => fetchJobs(true)} 
              disabled={isRefreshingHistory}
              className="refresh-btn"
              title="Tải lại danh sách"
            >
              <RefreshCw size={14} className={isRefreshingHistory ? 'spinner' : ''} />
            </button>
          </div>

          {isLoadingJobs ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem 0' }}>
              <div className="spinner" style={{ width: '20px', height: '20px' }}></div>
            </div>
          ) : jobsError ? (
            <div className="alert alert-error" style={{ fontSize: '0.75rem', padding: '0.5rem' }}>
              <AlertCircle size={14} />
              <span>{jobsError}</span>
            </div>
          ) : jobs.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '1.5rem', color: 'hsl(var(--text-muted))', fontSize: '0.78rem', border: '1px dashed var(--border-glass)', borderRadius: '12px' }}>
              Chưa có lịch sử submit.
            </div>
          ) : (
            <div className="audit-items-container" style={{ maxHeight: '450px', overflowY: 'auto', gap: '0.5rem' }}>
              {jobs.map((job) => {
                const isActiveJob = selectedJobId === job.jobId;
                return (
                  <div 
                    key={job.jobId} 
                    onClick={() => {
                      setSelectedJobId(job.jobId);
                      setSubmitError('');
                      setSubmitSuccess('');
                    }}
                    className={`audit-item-card ${isActiveJob ? 'active' : ''}`}
                    style={{ padding: '0.85rem', cursor: 'pointer', margin: 0 }}
                  >
                    <div className="audit-item-info">
                      <div className="audit-item-url" style={{ fontSize: '0.85rem' }}>{job.websiteUrl}</div>
                      <div className="audit-item-meta" style={{ fontSize: '0.68rem', gap: '4px' }}>
                        <span style={{ color: 'hsl(var(--text-secondary))' }}>
                          {job.details?.map(d => d.platformName).join(', ') || 'N/A'}
                        </span>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span className={`status-badge ${getStatusClass(job.status)}`} style={{ fontSize: '0.62rem', padding: '1px 4px' }}>
                        {job.status === 'Completed' || job.status === 'Success' ? 'Xong' : getStatusLabel(job.status)}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* RIGHT COLUMN (Wider Panel): Dynamic workspace - Platform grid & submit form, OR Job Details page */}
      <div className="dashboard-panel scrollable-panel" style={{ minHeight: '550px' }}>
        
        {/* Anti-spam confirmation dialog */}
        {showConfirmDialog && (
          <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
            <div style={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '16px', padding: '1.5rem', maxWidth: '400px', textAlign: 'center', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3)' }}>
              <ShieldCheck size={48} style={{ color: 'hsl(var(--accent-primary))', margin: '0 auto 1rem' }} />
              <h3 style={{ fontSize: '1.15rem', color: '#fff', marginBottom: '0.5rem' }}>Xác nhận Submit</h3>
              <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
                Gửi yêu cầu submit URL website tới platform <strong>{activePlatform?.name}</strong>.
              </p>
              <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
                <button
                  onClick={() => setShowConfirmDialog(false)}
                  className="btn btn-outline"
                  style={{ width: 'auto', padding: '0.5rem 1.25rem' }}
                >
                  Hủy bỏ
                </button>
                <button
                  onClick={executeSubmitJob}
                  className="btn btn-primary"
                  style={{ width: 'auto', padding: '0.5rem 1.25rem' }}
                >
                  Xác nhận
                </button>
              </div>
            </div>
          </div>
        )}

        {selectedJobId ? (
          /* ==========================================
             VIEW 1: DETAILED PROGRESS / CRAWL DETAILS 
             ========================================== */
          <div>
            <div className="detail-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid rgba(255,255,255,0.06)', paddingBottom: '1rem' }}>
              <button 
                onClick={() => setSelectedJobId(null)}
                className="btn btn-outline"
                style={{ width: 'auto', padding: '0.4rem 0.85rem', fontSize: '0.8rem', display: 'inline-flex', gap: '4px', margin: 0 }}
              >
                <ArrowLeft size={14} /> Trở lại danh mục
              </button>

              {jobDetails && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div className={`status-badge ${getStatusClass(jobDetails.status)}`} style={{ padding: '4px 10px', fontSize: '0.75rem' }}>
                    {getStatusLabel(jobDetails.status)}
                  </div>
                </div>
              )}
            </div>

            {isLoadingJobDetails ? (
              <div className="loading-screen" style={{ minHeight: '300px' }}>
                <div className="loading-dots"><div className="dot"></div><div className="dot"></div><div className="dot"></div></div>
                <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.85rem' }}>Đang tải tiến trình...</p>
              </div>
            ) : jobDetailsError ? (
              <div className="alert alert-error" style={{ marginTop: '1.5rem' }}>
                <AlertCircle size={18} />
                <span>{jobDetailsError}</span>
              </div>
            ) : jobDetails ? (
              <div style={{ marginTop: '1.25rem' }}>
                {/* Website overview card */}
                <div style={{ background: 'rgba(255,255,255,0.01)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '16px', padding: '1.25rem', marginBottom: '1.5rem' }}>
                  <span style={{ fontSize: '0.7rem', color: 'hsl(var(--text-muted))', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                    Website Submit
                  </span>
                  <h2 style={{ fontSize: '1.3rem', color: '#fff', fontWeight: 700, marginTop: '4px', wordBreak: 'break-all', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Globe size={20} style={{ color: 'hsl(var(--accent-primary))' }} />
                    <a href={jobDetails.websiteUrl} target="_blank" rel="noopener noreferrer" style={{ color: '#fff', textDecoration: 'none' }}>
                      {jobDetails.websiteUrl}
                    </a>
                    <ExternalLink size={14} style={{ color: 'hsl(var(--text-muted))' }} />
                  </h2>
                  <div style={{ fontSize: '0.75rem', color: 'hsl(var(--text-secondary))', marginTop: '6px' }}>
                    Tạo lúc: {new Date(jobDetails.createdAt).toLocaleString('vi-VN')}
                  </div>
                </div>

                <h3 style={{ fontSize: '0.95rem', color: '#fff', fontWeight: 600, marginBottom: '0.85rem', display: 'flex', gap: '6px', alignItems: 'center' }}>
                  <FileText size={16} /> Chi tiết platforms ({jobDetails.details?.length || 0})
                </h3>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                  {jobDetails.details.map(detail => {
                    const isExpanded = expandedDetailId === detail.detailId;
                    const isDetailStackShare = detail.platformCode?.toLowerCase() === 'stackshare';

                    // Parse crawled data
                    let crawledData = null;
                    if (detail.responseData) {
                      try {
                        const parsed = JSON.parse(detail.responseData);
                        if (parsed && parsed.crawled_data) {
                          crawledData = parsed.crawled_data;
                        }
                      } catch (e) {
                        // ResponseData isn't JSON
                      }
                    }

                    return (
                      <div 
                        key={detail.detailId} 
                        style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: '12px', overflow: 'hidden' }}
                      >
                        {/* Detail Platform Row Header */}
                        <div 
                          onClick={() => setExpandedDetailId(isExpanded ? null : detail.detailId)}
                          style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.85rem 1.25rem', cursor: 'pointer', userSelect: 'none' }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                            {detail.status === 'Success' || detail.status === 'Completed' ? (
                              <CheckCircle2 size={18} style={{ color: '#4ade80' }} />
                            ) : detail.status === 'Failed' ? (
                              <AlertCircle size={18} style={{ color: 'hsl(var(--accent-error))' }} />
                            ) : (
                              <div className="spinner" style={{ width: '15px', height: '15px', borderWidth: '2px' }}></div>
                            )}
                            <span style={{ fontSize: '0.9rem', fontWeight: 600, color: '#fff' }}>{detail.platformName}</span>
                            <span style={{ fontSize: '0.7rem', color: 'hsl(var(--text-muted))' }}>({detail.platformCode.toUpperCase()})</span>
                          </div>

                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span className={`status-badge ${getStatusClass(detail.status)}`} style={{ fontSize: '0.68rem', padding: '2px 8px' }}>
                              {getStatusLabel(detail.status)}
                            </span>
                            {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                          </div>
                        </div>

                        {/* Detail Collapsible Container */}
                        {isExpanded && (
                          <div style={{ padding: '1.25rem', borderTop: '1px solid rgba(255,255,255,0.06)', background: 'rgba(0,0,0,0.18)', fontSize: '0.8rem' }}>
                            
                            {detail.errorMessage && (
                              <div className="alert alert-error" style={{ padding: '0.6rem 0.85rem', fontSize: '0.75rem', marginBottom: '0.85rem', borderRadius: '6px' }}>
                                <AlertCircle size={14} />
                                <span>{detail.errorMessage}</span>
                              </div>
                            )}

                            {/* CRAWLED DATA PREVIEW FOR STACKSHARE */}
                            {isDetailStackShare && crawledData && (
                              <div style={{ marginBottom: '1.25rem', padding: '1rem', background: 'rgba(74, 222, 128, 0.04)', border: '1px solid rgba(74, 222, 128, 0.18)', borderRadius: '10px' }}>
                                <h4 style={{ fontSize: '0.85rem', color: '#4ade80', fontWeight: 600, marginBottom: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                  <CheckCircle2 size={15} /> Dữ liệu crawl trích xuất thành công:
                                </h4>
                                
                                <div style={{ display: 'grid', gridTemplateColumns: crawledData.logo ? '60px 1fr' : '1fr', gap: '1rem', alignItems: 'center', marginBottom: '1rem' }}>
                                  {crawledData.logo && (
                                    <img 
                                      src={crawledData.logo} 
                                      alt="Logo" 
                                      style={{ width: '60px', height: '60px', borderRadius: '10px', background: '#fff', objectFit: 'contain', padding: '4px', border: '1px solid rgba(255,255,255,0.1)' }}
                                      onError={(e) => e.currentTarget.style.display = 'none'}
                                    />
                                  )}
                                  <div>
                                    <div style={{ fontSize: '1rem', fontWeight: 700, color: '#fff' }}>
                                      {crawledData.tool_name || 'N/A'}
                                    </div>
                                    {crawledData.website_url && (
                                      <a href={crawledData.website_url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.75rem', color: 'hsl(var(--accent-primary))', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '3px' }}>
                                        {crawledData.website_url} <ExternalLink size={10} />
                                      </a>
                                    )}
                                  </div>
                                </div>

                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', fontSize: '0.8rem', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '0.75rem' }}>
                                  {crawledData.short_description && (
                                    <div>
                                      <span style={{ color: 'hsl(var(--text-secondary))', fontWeight: 600 }}>Mô tả ngắn:</span>{' '}
                                      <span style={{ color: 'hsl(var(--text-primary))' }}>{crawledData.short_description}</span>
                                    </div>
                                  )}
                                  {crawledData.description && (
                                    <div>
                                      <span style={{ color: 'hsl(var(--text-secondary))', fontWeight: 600 }}>Mô tả chi tiết:</span>{' '}
                                      <span style={{ color: 'hsl(var(--text-primary))' }}>{crawledData.description}</span>
                                    </div>
                                  )}
                                  {crawledData.features && (
                                    <div>
                                      <span style={{ color: 'hsl(var(--text-secondary))', fontWeight: 600 }}>Tính năng / Tag:</span>{' '}
                                      <span style={{ color: 'hsl(var(--text-primary))' }}>{crawledData.features}</span>
                                    </div>
                                  )}
                                  {crawledData.docs_url && (
                                    <div>
                                      <span style={{ color: 'hsl(var(--text-secondary))', fontWeight: 600 }}>Tài liệu (Docs):</span>{' '}
                                      <a href={crawledData.docs_url} target="_blank" rel="noopener noreferrer" style={{ color: 'hsl(var(--accent-primary))', textDecoration: 'none' }}>
                                        {crawledData.docs_url}
                                      </a>
                                    </div>
                                  )}
                                </div>

                                {/* Actions */}
                                <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
                                  <button
                                    type="button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      const pre = e.currentTarget.parentNode.nextElementSibling;
                                      pre.style.display = pre.style.display === 'none' ? 'block' : 'none';
                                    }}
                                    className="btn btn-outline"
                                    style={{ width: 'auto', padding: '4px 10px', fontSize: '0.7rem', display: 'inline-flex', gap: '4px', margin: 0 }}
                                  >
                                    <FileJson size={12} /> Xem JSON raw
                                  </button>
                                  <button
                                    type="button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      copyToClipboard(JSON.stringify(crawledData, null, 2), detail.detailId);
                                    }}
                                    className="btn btn-outline"
                                    style={{ width: 'auto', padding: '4px 10px', fontSize: '0.7rem', display: 'inline-flex', gap: '4px', margin: 0 }}
                                  >
                                    {copiedDataId === detail.detailId ? <Check size={12} style={{ color: '#4ade80' }} /> : <Copy size={12} />}
                                    {copiedDataId === detail.detailId ? 'Đã copy!' : 'Copy JSON'}
                                  </button>
                                </div>
                                <pre style={{ display: 'none', marginTop: '0.65rem', padding: '0.65rem', background: '#090d16', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '6px', fontSize: '0.72rem', color: '#94a3b8', overflowX: 'auto', fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                                  {JSON.stringify(crawledData, null, 2)}
                                </pre>
                              </div>
                            )}

                            {/* ASR direct HTTP logs */}
                            {!isDetailStackShare && detail.responseData && (
                              <div style={{ marginBottom: '1.25rem', padding: '0.85rem', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '8px' }}>
                                <span style={{ color: 'hsl(var(--text-secondary))', fontWeight: 600, fontSize: '0.75rem' }}>Phản hồi HTTP:</span>
                                <div style={{ color: 'hsl(var(--text-primary))', fontSize: '0.75rem', fontFamily: 'monospace', marginTop: '4px', wordBreak: 'break-all' }}>
                                  {detail.responseData}
                                </div>
                              </div>
                            )}

                            {/* Audit Logs Console */}
                            <div>
                              <div style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))', fontWeight: 600, marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                <Terminal size={12} /> NHẬT KÝ HOẠT ĐỘNG:
                              </div>
                              {detail.auditLogs?.length === 0 ? (
                                <div style={{ color: 'hsl(var(--text-muted))', fontStyle: 'italic', fontSize: '0.72rem' }}>Không có nhật ký.</div>
                              ) : (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontFamily: 'monospace', fontSize: '0.72rem', background: '#0f172a', padding: '0.65rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.03)', maxHeight: '180px', overflowY: 'auto' }}>
                                  {detail.auditLogs.map(log => (
                                    <div key={log.id} style={{ display: 'flex', flexDirection: 'column', padding: '2px 0', borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
                                      <div style={{ display: 'flex', justifyContent: 'space-between', color: log.status === 'Failed' ? 'hsl(var(--accent-error))' : log.status === 'Success' ? '#4ade80' : 'hsl(var(--accent-primary))' }}>
                                        <span>[{new Date(log.timestamp).toLocaleTimeString()}] {log.action} ({log.status})</span>
                                        {log.durationMs && <span>{log.durationMs}ms</span>}
                                      </div>
                                      {log.logContent && <div style={{ color: 'hsl(var(--text-secondary))', paddingLeft: '8px', marginTop: '2px', whiteSpace: 'pre-wrap' }}>{log.logContent}</div>}
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : null}
          </div>
        ) : (
          /* ==========================================
             VIEW 2: DYNAMIC PLATFORM CATALOG & SUBMIT FORM
             ========================================== */
          <div>
            {/* Catalog Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
              <div>
                <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff', background: 'linear-gradient(135deg, #fff 40%, hsl(var(--text-secondary)) 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', letterSpacing: '-0.5px' }}>
                  SEO Platforms Directory
                </h1>
                <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.85rem', marginTop: '2px' }}>
                  Chọn một platform bên dưới để tự động submit và khai báo chỉ mục cho website.
                </p>
              </div>
            </div>

            {/* Catalog Filters Bar (Uplizd style) */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: '12px', padding: '0.75rem 1rem', marginBottom: '1.5rem' }}>
              
              {/* Method filter toggle */}
              <div style={{ display: 'flex', gap: '4px', background: 'rgba(0,0,0,0.25)', padding: '3px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.04)' }}>
                <button
                  type="button"
                  onClick={() => setMethodFilter('ALL')}
                  style={{
                    background: methodFilter === 'ALL' ? 'rgba(255,255,255,0.08)' : 'none',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '4px 10px',
                    fontSize: '0.75rem',
                    color: methodFilter === 'ALL' ? '#fff' : 'hsl(var(--text-secondary))',
                    cursor: 'pointer',
                    fontWeight: 500
                  }}
                >
                  Tất cả
                </button>
                <button
                  type="button"
                  onClick={() => setMethodFilter('API')}
                  style={{
                    background: methodFilter === 'API' ? 'rgba(255,255,255,0.08)' : 'none',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '4px 10px',
                    fontSize: '0.75rem',
                    color: methodFilter === 'API' ? '#fff' : 'hsl(var(--text-secondary))',
                    cursor: 'pointer',
                    fontWeight: 500
                  }}
                >
                  Direct API
                </button>
                <button
                  type="button"
                  onClick={() => setMethodFilter('AUTOMATION')}
                  style={{
                    background: methodFilter === 'AUTOMATION' ? 'rgba(255,255,255,0.08)' : 'none',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '4px 10px',
                    fontSize: '0.75rem',
                    color: methodFilter === 'AUTOMATION' ? '#fff' : 'hsl(var(--text-secondary))',
                    cursor: 'pointer',
                    fontWeight: 500
                  }}
                >
                  UI Automation
                </button>
              </div>

              {/* Search bar */}
              <div style={{ position: 'relative', width: '220px' }}>
                <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'hsl(var(--text-muted))' }} />
                <input
                  type="text"
                  placeholder="Tìm platform..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '6px 10px 6px 30px',
                    borderRadius: '8px',
                    background: 'rgba(0, 0, 0, 0.25)',
                    border: '1px solid var(--border-glass)',
                    color: '#fff',
                    fontSize: '0.8rem',
                    outline: 'none'
                  }}
                />
              </div>
            </div>

            {/* Platform Grid (Uplizd style) */}
            {isLoadingPlatforms ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem 0' }}>
                <div className="spinner" style={{ width: '30px', height: '30px', borderWidth: '3.5px' }}></div>
              </div>
            ) : filteredPlatforms.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '3rem 1.5rem', color: 'hsl(var(--text-secondary))', border: '1px dashed rgba(255,255,255,0.06)', borderRadius: '16px' }}>
                Không tìm thấy platform nào khớp với từ khóa tìm kiếm hoặc bộ lọc.
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>
                {filteredPlatforms.map(platform => {
                  const isSelected = selectedPlatformId === platform.id;
                  const isSS = platform.code?.toLowerCase() === 'stackshare';
                  const meta = getPlatformMetadata(platform.code);
                  
                  return (
                    <div
                      key={platform.id}
                      onClick={() => {
                        setSelectedPlatformId(platform.id);
                        setSubmitError('');
                        setSubmitSuccess('');
                      }}
                      style={{
                        background: 'rgba(255, 255, 255, 0.02)',
                        border: isSelected ? '2px solid hsl(var(--accent-primary))' : '1px solid var(--border-glass)',
                        borderRadius: '20px',
                        padding: '1.25rem',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                        minHeight: '200px',
                        cursor: 'pointer',
                        position: 'relative',
                        transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
                        boxShadow: isSelected ? '0 10px 25px -5px hsl(var(--accent-primary) / 0.15)' : 'none',
                        transform: isSelected ? 'translateY(-4px)' : 'none',
                      }}
                    >
                      {/* Top Type Label */}
                      <span style={{
                        position: 'absolute',
                        top: '12px',
                        right: '12px',
                        fontSize: '0.62rem',
                        background: isSelected ? 'hsl(var(--accent-primary) / 0.15)' : 'rgba(255, 255, 255, 0.04)',
                        border: isSelected ? '1px solid hsl(var(--accent-primary) / 0.3)' : '1px solid var(--border-glass)',
                        padding: '2px 8px',
                        borderRadius: '9999px',
                        color: isSelected ? 'hsl(var(--accent-primary))' : 'hsl(var(--text-secondary))',
                        fontWeight: 600,
                        letterSpacing: '0.5px'
                      }}>
                        {meta.typeLabel}
                      </span>

                      {/* Header (Icon + Title) */}
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '0.75rem', width: '80%' }}>
                          <div style={{
                            width: '36px',
                            height: '36px',
                            borderRadius: '10px',
                            background: isSelected ? 'hsl(var(--accent-primary) / 0.1)' : 'rgba(255,255,255,0.03)',
                            border: isSelected ? '1px solid hsl(var(--accent-primary) / 0.2)' : '1px solid var(--border-glass)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: isSelected ? 'hsl(var(--accent-primary))' : 'hsl(var(--text-secondary))'
                          }}>
                            {isSS ? <Layers size={18} /> : <Globe size={18} />}
                          </div>
                          <span style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fff', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {platform.name}
                          </span>
                        </div>

                        {/* Tags */}
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '0.75rem' }}>
                          {meta.tags.map(tag => (
                            <span key={tag} style={{
                              fontSize: '0.62rem',
                              background: 'rgba(255, 255, 255, 0.03)',
                              border: '1px solid rgba(255, 255, 255, 0.05)',
                              padding: '1px 6px',
                              borderRadius: '4px',
                              color: 'hsl(var(--text-secondary))'
                            }}>
                              {tag}
                            </span>
                          ))}
                        </div>

                        {/* Description */}
                        <p style={{
                          fontSize: '0.75rem',
                          color: 'hsl(var(--text-secondary))',
                          lineHeight: 1.4,
                          marginBottom: '1rem',
                          display: '-webkit-box',
                          WebkitLineClamp: 3,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                          height: '3.2em'
                        }}>
                          {meta.description}
                        </p>
                      </div>

                      {/* Footer */}
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        borderTop: '1px solid rgba(255, 255, 255, 0.04)',
                        paddingTop: '0.75rem',
                        fontSize: '0.7rem',
                        color: 'hsl(var(--text-muted))'
                      }}>
                        <span>Tốc độ: {meta.speed}</span>
                        <span style={{
                          background: 'rgba(34, 197, 94, 0.08)',
                          border: '1px solid rgba(34, 197, 94, 0.15)',
                          color: '#4ade80',
                          padding: '1px 6px',
                          borderRadius: '4px',
                          fontWeight: 600
                        }}>
                          {meta.cost}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Submit Form Area (renders under catalog for the active selection) */}
            {activePlatform && (
              <div className="auth-container" style={{
                maxWidth: '100%',
                background: 'rgba(255, 255, 255, 0.03)',
                padding: '2rem',
                border: '1px solid rgba(255, 255, 255, 0.06)',
                borderRadius: '24px',
                marginTop: '2rem',
                animation: 'none'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid rgba(255,255,255,0.06)', paddingBottom: '0.75rem', marginBottom: '1.25rem' }}>
                  <h2 className="form-title" style={{ display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
                    {isActivePlatformStackShare ? <Layers size={20} className="input-icon-static" style={{ color: 'hsl(var(--accent-primary))' }} /> : <Globe size={20} className="input-icon-static" style={{ color: 'hsl(var(--accent-primary))' }} />}
                    {isActivePlatformAlternative
                      ? 'Submit Software to Alternative'
                      : isActivePlatformNewAIForYou
                        ? 'Submit Tool to New AI For You'
                      : isActivePlatformAwesomeIndie
                        ? 'Submit Product to Awesome Indie'
                      : isActivePlatformKyi
                        ? 'Submit AI Tool to Kyi AI'
                      : isActivePlatformFutureTools
                        ? 'Submit Tool to Future Tools'
                        : isActivePlatformTenWords
                          ? 'Submit Project to 10words'
                          : isActivePlatformBAI
                            ? 'Submit AI Tool to BAI.tools'
                            : `Submit Website to ${activePlatform.name}`}
                  </h2>
                </div>

                {isActivePlatformAlternative && (
                  <div style={{ marginBottom: '0.25rem', color: 'hsl(var(--text-secondary))', fontSize: '0.85rem', lineHeight: 1.5 }}>
                    Điền theo đúng form Alternative: Software Name ở bước đầu, rồi Category, Short/Full Description, Homepage URL, Pricing URL, Type, Monetization, Status, Platforms, Screenshots, Videos, Features, Social Links, Pricing và Synonyms ở form sau.
                  </div>
                )}

                {isActivePlatformNewAIForYou && (
                  <div style={{ marginBottom: '0.25rem', color: 'hsl(var(--text-secondary))', fontSize: '0.85rem', lineHeight: 1.5 }}>
                    New AI For You yêu cầu login Google trước, sau đó vào trang submit và chỉ cần điền Tool name + URL. Sau khi submit sẽ hiện modal rồi tự quay về trang home sau khoảng 6 giây.
                  </div>
                )}

                {isActivePlatformAwesomeIndie && (
                  <div style={{ marginBottom: '0.25rem', color: 'hsl(var(--text-secondary))', fontSize: '0.85rem', lineHeight: 1.5 }}>
                    Awesome Indie yêu cầu login Google trước, sau đó bấm AddProduct để vào form Submit. Điền Product name, URL, Tagline, Categories, Description, Social links và YouTube video URL rồi submit.
                  </div>
                )}

                {isActivePlatformTenWords && (
                  <div style={{ marginBottom: '0.25rem', color: 'hsl(var(--text-secondary))', fontSize: '0.85rem', lineHeight: 1.5 }}>
                    Điền đúng các field của 10words: Project Name, Project URL, Description, Twitter Handle, Category và Newsletter. Dữ liệu này sẽ được map trực tiếp vào worker.
                  </div>
                )}

                {isActivePlatformBAI && (
                  <div style={{ marginBottom: '0.25rem', color: 'hsl(var(--text-secondary))', fontSize: '0.85rem', lineHeight: 1.5 }}>
                    BAI.tools chỉ cần tên tool và website URL. Phần OAuth sẽ được xử lý ở bước xác thực riêng của worker.
                  </div>
                )}

                {isActivePlatformFutureTools && !isActivePlatformAlternative && (
                  <div style={{ marginBottom: '0.25rem', color: 'hsl(var(--text-secondary))', fontSize: '0.85rem', lineHeight: 1.5 }}>
                    Điền theo đúng form FutureTools: tên người submit, tên tool, URL, mô tả ngắn, category, pricing, email và checkbox newsletter.
                  </div>
                )}

                {isActivePlatformKyi && (
                  <div style={{ marginBottom: '0.25rem', color: 'hsl(var(--text-secondary))', fontSize: '0.85rem', lineHeight: 1.5 }}>
                    Kyi AI không cần đăng nhập. Chỉ cần điền Website Name, Website URL và Email rồi submit, hệ thống sẽ chờ pop-up success.
                  </div>
                )}

                <form onSubmit={handleFormSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                  {submitError && (
                    <div className="alert alert-error" style={{ padding: '0.65rem 0.85rem', marginBottom: 0 }}>
                      <AlertCircle size={16} />
                      <span style={{ fontSize: '0.8rem' }}>{submitError}</span>
                    </div>
                  )}
                  {submitSuccess && (
                    <div className="alert alert-success" style={{ padding: '0.65rem 0.85rem', marginBottom: 0 }}>
                      <CheckCircle2 size={16} />
                      <span style={{ fontSize: '0.8rem' }}>{submitSuccess}</span>
                    </div>
                  )}

                  {/* FORM FIELDS */}
                  {isActivePlatformAlternative && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      <div style={{ padding: '1rem', borderRadius: '14px', border: '1px solid rgba(255,255,255,0.08)', background: 'rgba(255,255,255,0.02)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                          <div>
                            <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff' }}>Tool mẫu đầy đủ</div>
                            <div style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))' }}>Bấm để đổ đầy toàn bộ dữ liệu vào form Alternative, rồi submit.</div>
                          </div>
                          <button
                            type="button"
                            onClick={fillAlternativeFullSample}
                            className="btn btn-primary"
                            style={{ width: 'auto', padding: '4px 10px', fontSize: '0.72rem', margin: 0 }}
                          >
                            Điền mẫu đầy đủ
                          </button>
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))' }}>
                          Các field bên dưới vẫn cho phép bạn chỉnh tay trước khi bấm Submit.
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Software Name *</label>
                        <div className="input-wrapper">
                          <FileText size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="Langflow"
                            value={siteName}
                            onChange={(e) => setSiteName(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.75rem' }}>
                          <label className="form-label" style={{ marginBottom: 0 }}>Short Description *</label>
                        </div>
                        <div className="input-wrapper" style={{ alignItems: 'flex-start' }}>
                          <FileText size={18} className="input-icon" style={{ marginTop: '0.7rem' }} />
                          <textarea
                            placeholder="Build and run LLM workflows with a visual builder for AI apps and automation."
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            className="form-input"
                            rows={3}
                            required
                          />
                        </div>
                        <div style={{ fontSize: '0.72rem', color: 'hsl(var(--text-muted))', marginTop: '0.35rem' }}>
                          Nên nhập ít nhất 100 ký tự để qua validation của Alternative.
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Full Description</label>
                        <div className="input-wrapper" style={{ alignItems: 'flex-start' }}>
                          <FileText size={18} className="input-icon" style={{ marginTop: '0.7rem' }} />
                          <textarea
                            placeholder="Langflow is a low-code platform for designing, testing, and deploying LLM workflows with reusable components, integrations, and API support."
                            value={alternativeFullDescription}
                            onChange={(e) => setAlternativeFullDescription(e.target.value)}
                            className="form-input"
                            rows={5}
                          />
                        </div>
                        <div style={{ fontSize: '0.72rem', color: 'hsl(var(--text-muted))', marginTop: '0.35rem' }}>
                          Nên nhập ít nhất 200 ký tự để qua validation của Alternative.
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Icon Path *</label>
                        <div className="input-wrapper">
                          <FileText size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="/Users/.../alternative-icon.png"
                            value={alternativeIconPath}
                            onChange={(e) => setAlternativeIconPath(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                        <div style={{ fontSize: '0.72rem', color: 'hsl(var(--text-muted))', marginTop: '0.35rem' }}>
                          Đây là đường dẫn file ảnh local để worker upload vào trường Icon.
                        </div>
                      </div>

                      <div style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))', marginTop: '-0.25rem' }}>
                        Icon đã được map bằng đường dẫn file local. Screenshots và Videos hiện vẫn chưa tự động điền.
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label className="form-label">Category *</label>
                          <select className="form-input" value={alternativeCategory} onChange={(e) => setAlternativeCategory(e.target.value)} required>
                            {[
                              { value: 'software/business/analytics', label: 'Business > Analytics' },
                              { value: 'software/business/productivity-and-communications', label: 'Business > Productivity and Communications' },
                              { value: 'software/business/customer-support-and-management', label: 'Business > Customer Support and Management' },
                              { value: 'software/business/finance-and-accounting', label: 'Business > Finance and Accounting' },
                              { value: 'software/business/human-resources', label: 'Business > Human Resources' },
                              { value: 'software/business/it-and-operations', label: 'Business > IT and Operations' },
                              { value: 'software/business/marketing', label: 'Business > Marketing' },
                              { value: 'software/business/design', label: 'Business > Design' },
                              { value: 'software/business/sales', label: 'Business > Sales' },
                              { value: 'software/desktop/business', label: 'Desktop > Business' },
                              { value: 'software/desktop/tools', label: 'Desktop > Tools' },
                              { value: 'software/desktop/social', label: 'Desktop > Social' },
                              { value: 'software/desktop/knowledge', label: 'Desktop > Knowledge' },
                              { value: 'software/desktop/security', label: 'Desktop > Security' },
                              { value: 'software/desktop/media', label: 'Desktop > Media' },
                              { value: 'software/desktop/development', label: 'Desktop > Development' },
                              { value: 'software/desktop/games', label: 'Desktop > Games' },
                              { value: 'software/desktop/kids', label: 'Desktop > Kids' },
                              { value: 'software/desktop/travel', label: 'Desktop > Travel' },
                              { value: 'software/desktop/news', label: 'Desktop > News' },
                              { value: 'software/desktop/health', label: 'Desktop > Health' },
                              { value: 'software/desktop/lifestyle', label: 'Desktop > Lifestyle' },
                              { value: 'software/mobile/books', label: 'Mobile > Books' },
                              { value: 'software/mobile/business', label: 'Mobile > Business' },
                              { value: 'software/mobile/education', label: 'Mobile > Education' },
                              { value: 'software/mobile/entertainment', label: 'Mobile > Entertainment' },
                              { value: 'software/mobile/finance', label: 'Mobile > Finance' },
                              { value: 'software/mobile/food-drink', label: 'Mobile > Food & Drink' },
                              { value: 'software/mobile/games', label: 'Mobile > Games' },
                              { value: 'software/mobile/health-fitness', label: 'Mobile > Health & Fitness' },
                              { value: 'software/mobile/lifestyle', label: 'Mobile > Lifestyle' },
                              { value: 'software/mobile/kids', label: 'Mobile > Kids' },
                              { value: 'software/mobile/magazines-newspapers', label: 'Mobile > Magazines & Newspapers' },
                              { value: 'software/mobile/medical', label: 'Mobile > Medical' },
                              { value: 'software/mobile/music', label: 'Mobile > Music' },
                              { value: 'software/mobile/navigation', label: 'Mobile > Navigation' },
                              { value: 'software/mobile/news', label: 'Mobile > News' },
                              { value: 'software/mobile/photo-video', label: 'Mobile > Photo & Video' },
                              { value: 'software/mobile/productivity', label: 'Mobile > Productivity' },
                              { value: 'software/mobile/reference', label: 'Mobile > Reference' },
                              { value: 'software/mobile/shopping', label: 'Mobile > Shopping' },
                              { value: 'software/mobile/social-networking', label: 'Mobile > Social Networking' },
                              { value: 'software/mobile/sports', label: 'Mobile > Sports' },
                              { value: 'software/mobile/travel', label: 'Mobile > Travel' },
                              { value: 'software/mobile/utilities', label: 'Mobile > Utilities' },
                              { value: 'software/mobile/weather', label: 'Mobile > Weather' },
                              { value: 'software/mobile/widget', label: 'Mobile > Widget' },
                              { value: 'software/web/business', label: 'Web > Business' },
                              { value: 'software/web/tools', label: 'Web > Tools' },
                              { value: 'software/web/social', label: 'Web > Social' },
                              { value: 'software/web/knowledge', label: 'Web > Knowledge' },
                              { value: 'software/web/security', label: 'Web > Security' },
                              { value: 'software/web/media', label: 'Web > Media' },
                              { value: 'software/web/development', label: 'Web > Development' },
                              { value: 'software/web/games', label: 'Web > Games' },
                              { value: 'software/web/kids', label: 'Web > Kids' },
                              { value: 'software/web/travel', label: 'Web > Travel' },
                              { value: 'software/web/news', label: 'Web > News' },
                              { value: 'software/web/health', label: 'Web > Health' },
                              { value: 'software/web/lifestyle', label: 'Web > Lifestyle' },
                              { value: 'software/os/os', label: 'Software > Operating System' },
                            ].map((option) => (
                              <option key={option.value} value={option.value}>{option.label}</option>
                            ))}
                          </select>
                        </div>

                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label className="form-label">Homepage URL *</label>
                          <div className="input-wrapper">
                            <Globe size={18} className="input-icon" />
                            <input
                              type="text"
                              placeholder="https://example.com"
                              value={url}
                              onChange={(e) => setUrl(e.target.value)}
                              className="form-input"
                              required
                            />
                          </div>
                        </div>

                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label className="form-label">Pricing URL</label>
                          <div className="input-wrapper">
                            <Globe size={18} className="input-icon" />
                            <input
                              type="text"
                              placeholder="Pricing URL"
                              value={alternativePricingUrl}
                              onChange={(e) => setAlternativePricingUrl(e.target.value)}
                              className="form-input"
                            />
                          </div>
                        </div>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label className="form-label">Type</label>
                          <select className="form-input" value={alternativeType} onChange={(e) => setAlternativeType(e.target.value)}>
                            {[
                              { value: 'desktop', label: 'Desktop Client' },
                              { value: 'app', label: 'App' },
                              { value: 'online', label: 'Online / SaaS' },
                            ].map((option) => (
                              <option key={option.value} value={option.value}>{option.label}</option>
                            ))}
                          </select>
                        </div>

                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label className="form-label">Monetization</label>
                          <select className="form-input" value={alternativeMonetization} onChange={(e) => setAlternativeMonetization(e.target.value)}>
                            {[
                              { value: 'opensource', label: 'Open Source' },
                              { value: 'free', label: 'Free' },
                              { value: 'freemium', label: 'Freemium' },
                              { value: 'paid', label: 'Paid' },
                            ].map((option) => (
                              <option key={option.value} value={option.value}>{option.label}</option>
                            ))}
                          </select>
                        </div>

                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label className="form-label">Status</label>
                          <select className="form-input" value={alternativeStatus} onChange={(e) => setAlternativeStatus(e.target.value)}>
                            {[
                              { value: 'announced', label: 'Announced' },
                              { value: 'live', label: 'Released' },
                              { value: 'abandoned', label: 'Abandoned' },
                              { value: 'offline', label: 'Offline' },
                            ].map((option) => (
                              <option key={option.value} value={option.value}>{option.label}</option>
                            ))}
                          </select>
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Platforms</label>
                        <div className="input-wrapper">
                          <input
                            type="text"
                            placeholder="Please select all matching platforms from the list below."
                            value={alternativePlatforms}
                            onChange={(e) => setAlternativePlatforms(e.target.value)}
                            className="form-input"
                          />
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))', marginTop: '0.4rem' }}>
                          Nhập danh sách nền tảng rồi bấm Enter hoặc Add Platform ở form gốc. UI sẽ gửi chuỗi này cho worker để tách thành tag.
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Features</label>
                        <div className="input-wrapper">
                          <input
                            type="text"
                            placeholder="Start typing features and click to select ..."
                            value={alternativeFeatures}
                            onChange={(e) => setAlternativeFeatures(e.target.value)}
                            className="form-input"
                          />
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))', marginTop: '0.4rem' }}>
                          Nhập các feature cách nhau bằng dấu phẩy, worker sẽ tự gửi lần lượt.
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Social Links</label>
                        <div style={{ display: 'grid', gridTemplateColumns: '160px 1fr auto', gap: '0.75rem', alignItems: 'center' }}>
                          <select className="form-input" value={alternativeSocialLinkType} onChange={(e) => setAlternativeSocialLinkType(e.target.value)}>
                            {[
                              { value: 'angellist', label: 'AngelList' },
                              { value: 'facebook', label: 'Facebook' },
                              { value: 'github', label: 'GitHub' },
                              { value: 'instagram', label: 'Instagram' },
                              { value: 'medium-platform', label: 'Medium' },
                              { value: 'steam', label: 'Steam' },
                              { value: 'source', label: 'Source' },
                              { value: 'twitter', label: 'Twitter' },
                              { value: 'discord', label: 'Discord' },
                            ].map((option) => (
                              <option key={option.value} value={option.value}>{option.label}</option>
                            ))}
                          </select>
                          <input
                            type="text"
                            placeholder="https://..."
                            value={alternativeSocialLinkUrl}
                            onChange={(e) => setAlternativeSocialLinkUrl(e.target.value)}
                            className="form-input"
                          />
                          <button type="button" className="btn btn-primary" style={{ width: 'auto', padding: '0.65rem 1rem' }} onClick={handleAddAlternativeSocialLink}>
                            Add Link
                          </button>
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))', marginTop: '0.4rem' }}>
                          Form thật yêu cầu chọn Link Type rồi bấm Add Link. UI này hiển thị đúng cấu trúc đó.
                        </div>
                        {alternativeSocialLinks && (
                          <div style={{ fontSize: '0.75rem', color: 'hsl(var(--text-secondary))', marginTop: '0.4rem' }}>
                            Đã thêm: {alternativeSocialLinks}
                          </div>
                        )}
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label className="form-label">Pricing Name</label>
                          <input
                            type="text"
                            placeholder="Premium"
                            value={alternativePricingName}
                            onChange={(e) => setAlternativePricingName(e.target.value)}
                            className="form-input"
                          />
                        </div>

                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label className="form-label">Pricing Cost</label>
                          <input
                            type="text"
                            placeholder="Cost per month (USD)"
                            value={alternativePricingCost}
                            onChange={(e) => setAlternativePricingCost(e.target.value)}
                            className="form-input"
                          />
                        </div>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                        <button type="button" className="btn btn-primary" style={{ width: 'auto', padding: '0.65rem 1rem' }}>
                          Add Pricing
                        </button>
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))', marginTop: '-0.6rem' }}>
                        Nhập xong Pricing Name/Cost rồi bấm Add Pricing trên form thật.
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Synonyms</label>
                        <div className="input-wrapper">
                          <input
                            type="text"
                            placeholder="Add synonyms and press Enter..."
                            value={alternativeSynonyms}
                            onChange={(e) => setAlternativeSynonyms(e.target.value)}
                            className="form-input"
                          />
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))', marginTop: '0.4rem' }}>
                          Đây là tag input, nhập từng cụm rồi bấm Enter.
                        </div>
                      </div>

                    </div>
                  )}

                  {isActivePlatformKyi && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      <div style={{
                        padding: '1rem 1.1rem',
                        borderRadius: '16px',
                        border: '1px solid rgba(34, 197, 94, 0.18)',
                        background: 'linear-gradient(135deg, rgba(34,197,94,0.08), rgba(255,255,255,0.02))'
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', flexWrap: 'wrap' }}>
                          <div style={{ minWidth: '220px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.35rem' }}>
                              <Send size={16} style={{ color: 'hsl(var(--accent-primary))' }} />
                              <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#fff' }}>Kyi AI Submit Form</div>
                            </div>
                            <div style={{ fontSize: '0.8rem', color: 'hsl(var(--text-secondary))', lineHeight: 1.5 }}>
                              Form public, không cần login. UI sẽ gửi đúng 3 field và đợi pop-up success sau khi submit.
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Website Name *</label>
                        <div className="input-wrapper">
                          <FileText size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="Kyi AI"
                            value={siteName}
                            onChange={(e) => setSiteName(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Website URL *</label>
                        <div className="input-wrapper">
                          <Globe size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="https://kyi.ai"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Email *</label>
                        <div className="input-wrapper">
                          <Mail size={18} className="input-icon" />
                          <input
                            type="email"
                            placeholder="support@kyi.ai"
                            value={contactEmail}
                            onChange={(e) => setContactEmail(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>
                    </div>
                  )}

                  {isActivePlatformNewAIForYou && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      <div style={{
                        padding: '1rem 1.1rem',
                        borderRadius: '16px',
                        border: '1px solid rgba(168, 85, 247, 0.18)',
                        background: 'linear-gradient(135deg, rgba(168,85,247,0.10), rgba(255,255,255,0.02))'
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', flexWrap: 'wrap' }}>
                          <div style={{ minWidth: '220px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.35rem' }}>
                              <Send size={16} style={{ color: '#a855f7' }} />
                              <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#fff' }}>New AI For You Submit Form</div>
                            </div>
                            <div style={{ fontSize: '0.8rem', color: 'hsl(var(--text-secondary))', lineHeight: 1.5 }}>
                              Login Google trước, rồi worker sẽ vào trang submit, điền Tool name + URL, chờ modal success và quay về home sau 6 giây.
                            </div>
                          </div>

                          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                            <button
                              type="button"
                              className="btn btn-outline"
                              style={{ width: 'auto', padding: '0.5rem 0.85rem', margin: 0 }}
                              onClick={fillNewAIForYouDemoSample}
                            >
                              Demo data
                            </button>
                          </div>
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Tool name *</label>
                        <div className="input-wrapper">
                          <FileText size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="Langflow"
                            value={siteName}
                            onChange={(e) => setSiteName(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">URL *</label>
                        <div className="input-wrapper">
                          <Globe size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="https://www.langflow.org"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>
                    </div>
                  )}

                  {isActivePlatformAwesomeIndie && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      <div style={{
                        padding: '1rem 1.1rem',
                        borderRadius: '16px',
                        border: '1px solid rgba(245, 158, 11, 0.18)',
                        background: 'linear-gradient(135deg, rgba(245,158,11,0.10), rgba(255,255,255,0.02))'
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', flexWrap: 'wrap' }}>
                          <div style={{ minWidth: '220px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.35rem' }}>
                              <Send size={16} style={{ color: '#f59e0b' }} />
                              <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#fff' }}>Awesome Indie Submit Form</div>
                            </div>
                            <div style={{ fontSize: '0.8rem', color: 'hsl(var(--text-secondary))', lineHeight: 1.5 }}>
                              Login Google trước, bấm AddProduct rồi worker sẽ điền form tạo product và chờ phản hồi từ API post-product.
                            </div>
                          </div>

                          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                            <button
                              type="button"
                              className="btn btn-outline"
                              style={{ width: 'auto', padding: '0.5rem 0.85rem', margin: 0 }}
                              onClick={fillAwesomeIndieDemoSample}
                            >
                              Demo data
                            </button>
                          </div>
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Product Name *</label>
                        <div className="input-wrapper">
                          <FileText size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="Langflow"
                            value={siteName}
                            onChange={(e) => setSiteName(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">URL *</label>
                        <div className="input-wrapper">
                          <Globe size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="https://www.langflow.org"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Tagline *</label>
                        <div className="input-wrapper">
                          <FileText size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="Build and ship LLM workflows visually"
                            value={awesomeIndieTagline}
                            onChange={(e) => setAwesomeIndieTagline(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Categories *</label>
                        <div className="input-wrapper">
                          <Layers size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="AI Tools, Productivity"
                            value={awesomeIndieCategories}
                            onChange={(e) => setAwesomeIndieCategories(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))', marginTop: '0.35rem' }}>
                          Worker sẽ thử map theo text hoặc lấy category đầu tiên từ API `/api/categories/get-categories` nếu cần.
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Description *</label>
                        <div className="input-wrapper" style={{ alignItems: 'flex-start' }}>
                          <FileText size={18} className="input-icon" style={{ marginTop: '0.7rem' }} />
                          <textarea
                            placeholder="Langflow is a low-code platform for designing, testing, and deploying LLM workflows..."
                            value={awesomeIndieDescription}
                            onChange={(e) => setAwesomeIndieDescription(e.target.value)}
                            className="form-input"
                            rows={4}
                            required
                          />
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Social Links</label>
                        <div className="input-wrapper" style={{ alignItems: 'flex-start' }}>
                          <Globe size={18} className="input-icon" style={{ marginTop: '0.7rem' }} />
                          <textarea
                            placeholder="https://x.com/..., https://github.com/..."
                            value={awesomeIndieSocialLinks}
                            onChange={(e) => setAwesomeIndieSocialLinks(e.target.value)}
                            className="form-input"
                            rows={3}
                          />
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">YouTube Video URL</label>
                        <div className="input-wrapper">
                          <ExternalLink size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="https://www.youtube.com/watch?v=..."
                            value={awesomeIndieYouTubeVideoUrl}
                            onChange={(e) => setAwesomeIndieYouTubeVideoUrl(e.target.value)}
                            className="form-input"
                          />
                        </div>
                      </div>
                    </div>
                  )}

                  {isActivePlatformTenWords && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      <div style={{
                        padding: '1rem 1.1rem',
                        borderRadius: '16px',
                        border: '1px solid rgba(59, 130, 246, 0.18)',
                        background: 'linear-gradient(135deg, rgba(59,130,246,0.08), rgba(255,255,255,0.02))'
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', flexWrap: 'wrap' }}>
                          <div style={{ minWidth: '220px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.35rem' }}>
                              <Send size={16} style={{ color: 'hsl(var(--accent-primary))' }} />
                              <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#fff' }}>10words Submit Form</div>
                            </div>
                            <div style={{ fontSize: '0.8rem', color: 'hsl(var(--text-secondary))', lineHeight: 1.5 }}>
                              Form này map trực tiếp vào payload gửi lên worker hoặc API của 10words. Chỉ cần điền 5 trường chính là đủ.
                            </div>
                          </div>

                          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                            <button
                              type="button"
                              className="btn btn-outline"
                              style={{ width: 'auto', padding: '0.5rem 0.85rem', margin: 0 }}
                              onClick={fillTenWordsQuickSample}
                            >
                              Quick fill
                            </button>
                            <button
                              type="button"
                              className="btn btn-primary"
                              style={{ width: 'auto', padding: '0.5rem 0.85rem', margin: 0 }}
                              onClick={fillTenWordsDemoSample}
                            >
                              Demo data
                            </button>
                          </div>
                        </div>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.3fr) minmax(280px, 0.9fr)', gap: '1rem', alignItems: 'start' }}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                          <div className="form-group" style={{ marginBottom: 0 }}>
                            <label className="form-label">Project Name *</label>
                            <div className="input-wrapper">
                              <FileText size={18} className="input-icon" />
                              <input
                                type="text"
                                placeholder="Langflow"
                                value={siteName}
                                onChange={(e) => setSiteName(e.target.value)}
                                className="form-input"
                                required
                              />
                            </div>
                          </div>

                          <div className="form-group" style={{ marginBottom: 0 }}>
                            <label className="form-label">Project URL *</label>
                            <div className="input-wrapper">
                              <Globe size={18} className="input-icon" />
                              <input
                                type="text"
                                placeholder="https://www.langflow.org"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                className="form-input"
                                required
                              />
                            </div>
                          </div>

                          <div className="form-group" style={{ marginBottom: 0 }}>
                            <label className="form-label">Description *</label>
                            <div className="input-wrapper" style={{ alignItems: 'flex-start' }}>
                              <FileText size={18} className="input-icon" style={{ marginTop: '0.7rem' }} />
                              <textarea
                                placeholder="Describe your project in 10 words or less!"
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                className="form-input"
                                rows={4}
                                required
                              />
                            </div>
                          </div>

                          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                            <div className="form-group" style={{ marginBottom: 0 }}>
                              <label className="form-label">Category *</label>
                              <select
                                className="form-input"
                                value={tenWordsCategory}
                                onChange={(e) => setTenWordsCategory(e.target.value)}
                                required
                              >
                                {['Website', 'Mobile App', 'SaaS', 'Newsletter', 'Other'].map((option) => (
                                  <option key={option} value={option}>{option}</option>
                                ))}
                              </select>
                            </div>

                            <div className="form-group" style={{ marginBottom: 0 }}>
                              <label className="form-label">Twitter Handle</label>
                              <input
                                type="text"
                                placeholder="@langflow"
                                value={tenWordsTwitterHandle}
                                onChange={(e) => setTenWordsTwitterHandle(e.target.value)}
                                className="form-input"
                              />
                            </div>
                          </div>

                          <div className="form-group" style={{ marginBottom: 0 }}>
                            <label className="form-label">Newsletter</label>
                            <select
                              className="form-input"
                              value={tenWordsNewsletter}
                              onChange={(e) => setTenWordsNewsletter(e.target.value)}
                            >
                              {['No thanks', 'Daily', 'Daily (Mon-Thu)', 'Weekly', 'Weekly Digest'].map((option) => (
                                <option key={option} value={option}>{option}</option>
                              ))}
                            </select>
                          </div>
                        </div>

                        <div style={{
                          borderRadius: '16px',
                          border: '1px solid rgba(255,255,255,0.06)',
                          background: 'rgba(255,255,255,0.02)',
                          padding: '1rem',
                          position: 'sticky',
                          top: '1rem'
                        }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                            <div>
                              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#fff' }}>Payload Preview</div>
                              <div style={{ fontSize: '0.72rem', color: 'hsl(var(--text-muted))' }}>Dữ liệu sẽ được map sang worker.</div>
                            </div>
                            <button
                              type="button"
                              className="btn btn-outline"
                              style={{ width: 'auto', padding: '0.35rem 0.65rem', margin: 0, fontSize: '0.72rem' }}
                              onClick={() => copyToClipboard(JSON.stringify(tenWordsPreviewData, null, 2), 'tenwords-preview')}
                            >
                              {copiedDataId === 'tenwords-preview' ? <Check size={12} /> : <Copy size={12} />}
                              {copiedDataId === 'tenwords-preview' ? 'Copied' : 'Copy JSON'}
                            </button>
                          </div>

                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: '0.75rem' }}>
                            {['Project Name', 'Project URL', 'Description', 'Category', 'Newsletter'].map((label) => (
                              <span
                                key={label}
                                style={{
                                  fontSize: '0.64rem',
                                  padding: '2px 7px',
                                  borderRadius: '999px',
                                  background: 'rgba(59,130,246,0.08)',
                                  color: 'hsl(var(--accent-primary))',
                                  border: '1px solid rgba(59,130,246,0.14)'
                                }}
                              >
                                {label}
                              </span>
                            ))}
                          </div>

                          <pre style={{
                            margin: 0,
                            padding: '0.9rem',
                            borderRadius: '12px',
                            background: '#0b1120',
                            border: '1px solid rgba(255,255,255,0.05)',
                            color: '#cbd5e1',
                            fontSize: '0.72rem',
                            overflowX: 'auto',
                            whiteSpace: 'pre-wrap',
                            lineHeight: 1.45,
                            minHeight: '260px'
                          }}>
                            {JSON.stringify(tenWordsPreviewData, null, 2)}
                          </pre>

                          <div style={{ marginTop: '0.75rem', fontSize: '0.72rem', color: 'hsl(var(--text-muted))', lineHeight: 1.5 }}>
                            Nếu bạn submit bằng API token, worker sẽ bỏ qua browser và gửi trực tiếp lên <code style={{ color: '#fff' }}>app.10words.io/startups/</code>.
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {isActivePlatformBAI && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">AI Tool Name *</label>
                        <div className="input-wrapper">
                          <FileText size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="What is the name of your AI tool?"
                            value={siteName}
                            onChange={(e) => setSiteName(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Website URL *</label>
                        <div className="input-wrapper">
                          <Globe size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="https://example.com"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>
                    </div>
                  )}

                  {isActivePlatformFutureTools ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Your Name *</label>
                        <div className="input-wrapper">
                          <FileText size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="Jane Doe"
                            value={submitterName}
                            onChange={(e) => setSubmitterName(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Tool Name *</label>
                        <div className="input-wrapper">
                          <FileText size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="e.g. ChatGPT"
                            value={siteName}
                            onChange={(e) => setSiteName(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Tool URL *</label>
                        <div className="input-wrapper">
                          <Globe size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="https://your-tool.com"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Short Description *</label>
                        <div className="input-wrapper" style={{ alignItems: 'flex-start' }}>
                          <FileText size={18} className="input-icon" style={{ marginTop: '0.7rem' }} />
                          <textarea
                            placeholder="Briefly describe what the tool does..."
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            className="form-input"
                            rows={4}
                            required
                          />
                        </div>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label className="form-label">Category *</label>
                          <select
                            className="form-input"
                            value={futureToolsCategory}
                            onChange={(e) => setFutureToolsCategory(e.target.value)}
                          >
                            {['Chat', 'Generative Art', 'Generative Video', 'Generative Code', 'Text-To-Speech', 'Search Engines', 'Productivity', 'Marketing', 'Design', 'Writing', 'Music', 'Research', 'Education', 'Finance', 'Healthcare', 'Legal', 'Sales', 'Customer Support', 'Other'].map((option) => (
                              <option key={option} value={option}>{option}</option>
                            ))}
                          </select>
                        </div>

                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label className="form-label">Pricing *</label>
                          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                            {['Free', 'Freemium', 'Paid', 'Open Source'].map((option) => {
                              const active = futureToolsPricing === option;
                              return (
                                <button
                                  key={option}
                                  type="button"
                                  onClick={() => setFutureToolsPricing(option)}
                                  className="btn btn-outline"
                                  style={{
                                    width: 'auto',
                                    padding: '0.45rem 0.75rem',
                                    borderColor: active ? 'hsl(var(--accent-primary))' : undefined,
                                    color: active ? '#fff' : undefined,
                                    background: active ? 'hsl(var(--accent-primary) / 0.12)' : undefined,
                                  }}
                                >
                                  {option}
                                </button>
                              );
                            })}
                          </div>
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Your Email *</label>
                        <div className="input-wrapper">
                          <Mail size={18} className="input-icon" />
                          <input
                            type="email"
                            placeholder="you@example.com"
                            value={contactEmail}
                            onChange={(e) => setContactEmail(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>

                      <label style={{ display: 'flex', alignItems: 'flex-start', gap: '0.6rem', cursor: 'pointer', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '12px', padding: '0.85rem 1rem' }}>
                        <input
                          type="checkbox"
                          checked={futureToolsNewsletterOptIn}
                          onChange={(e) => setFutureToolsNewsletterOptIn(e.target.checked)}
                          style={{ marginTop: '0.15rem' }}
                        />
                        <span style={{ fontSize: '0.85rem', color: 'hsl(var(--text-secondary))' }}>
                          Join the Future Tools newsletter for AI news and tool recommendations. (Optional)
                        </span>
                      </label>
                    </div>
                  ) : (
                    <div style={{ display: 'grid', gridTemplateColumns: isActivePlatformASR ? '1fr 1fr' : '1fr', gap: '1rem' }}>
                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Website URL cần submit *</label>
                        <div className="input-wrapper">
                          <Globe size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="https://example.com"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>

                      {isActivePlatformASR && (
                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label className="form-label">Email liên hệ (Contact Email) *</label>
                          <div className="input-wrapper">
                            <Mail size={18} className="input-icon" />
                            <input
                              type="email"
                              placeholder="admin@example.com"
                              value={contactEmail}
                              onChange={(e) => setContactEmail(e.target.value)}
                              className="form-input"
                              required
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* StackShare Session import form inside the form wrapper */}
                  {isActivePlatformStackShare && (
                    <div style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '1rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                        <span style={{ fontSize: '0.8rem', color: 'hsl(var(--text-secondary))', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Lock size={14} style={{ color: 'hsl(var(--accent-primary))' }} /> Cấu hình Automation Browser Session
                        </span>
                        <button
                          type="button"
                          onClick={() => {
                            setActiveSettingsPlatformId(
                              activeSettingsPlatformId === activePlatform.id ? null : activePlatform.id
                            );
                            setConnectSuccess('');
                            setConnectError('');
                          }}
                          className="refresh-btn"
                          style={{ padding: '2px', color: activeSettingsPlatformId ? 'hsl(var(--accent-primary))' : 'inherit' }}
                          title="Import Playwright Session JSON"
                        >
                          <Settings size={14} />
                        </button>
                      </div>

                      {activeSettingsPlatformId === activePlatform.id ? (
                        <div style={{ background: 'rgba(59, 130, 246, 0.05)', border: '1px solid rgba(59, 130, 246, 0.12)', borderRadius: '12px', padding: '1rem', marginBottom: '1rem' }}>
                          <div style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))', lineHeight: 1.4, marginBottom: '0.65rem' }}>
                            Chạy Playwright local, lưu file <code>stackshare_storage_state.json</code>, rồi upload JSON đó vào đây để tự động hóa đăng nhập.
                          </div>
                          
                          {connectError && <div style={{ color: 'hsl(var(--accent-error))', fontSize: '0.75rem', marginBottom: '4px' }}>{connectError}</div>}
                          {connectSuccess && <div style={{ color: '#4ade80', fontSize: '0.75rem', marginBottom: '4px' }}>{connectSuccess}</div>}
                          
                          <div style={{ marginBottom: '0.75rem' }}>
                            <input
                              type="file"
                              accept="application/json,.json"
                              onChange={(e) => setSessionFile(e.target.files?.[0] || null)}
                              style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))' }}
                            />
                          </div>

                          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                            <button
                              type="button"
                              onClick={() => setActiveSettingsPlatformId(null)}
                              style={{ background: 'none', border: 'none', color: 'hsl(var(--text-muted))', fontSize: '0.75rem', cursor: 'pointer', padding: '4px 8px' }}
                            >
                              Hủy
                            </button>
                            <button
                              type="button"
                              disabled={isConnectingPlatform}
                              onClick={() => handleImportPlatformSession(activePlatform.id)}
                              className="btn btn-primary"
                              style={{ padding: '4px 12px', fontSize: '0.75rem', width: 'auto' }}
                            >
                              {isConnectingPlatform ? 'Đang import...' : 'Import'}
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div style={{ fontSize: '0.72rem', color: 'hsl(var(--text-muted))', fontStyle: 'italic' }}>
                          * Platform này sử dụng Chromium UI Automation chạy ngầm để điền form tự động.
                        </div>
                      )}
                    </div>
                  )}

                  {/* Submit buttons */}
                  <div style={{ display: 'flex', justifyContent: 'flex-end', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '1rem' }}>
                    <button
                      type="submit"
                      disabled={isSubmittingJob}
                      className="btn btn-primary"
                      style={{ width: 'auto', padding: '0.75rem 2rem', fontSize: '0.9rem' }}
                    >
                      {isSubmittingJob ? (
                        <div className="spinner"></div>
                      ) : (
                        <>
                          <Send size={16} />
                          {isActivePlatformFutureTools
                            ? 'Submit Tool'
                            : isActivePlatformKyi
                              ? 'Submit AI Tool'
                              : isActivePlatformTenWords
                                ? 'Submit Project'
                                : isActivePlatformBAI
                                  ? 'Submit AI Tool'
                                  : isActivePlatformStackShare
                                    ? 'Crawl & Submit Website'
                                    : 'Submit Website Direct'}
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
