import {
  Bot,
  Code2,
  Compass,
  Globe2,
  Layers3,
  Rocket,
  SearchCheck,
  Sparkles,
  Wrench,
} from 'lucide-react';

export const PLATFORM_BLUEPRINTS = {
  kyi_ai: {
    aliases: ['kyi', 'kyiai'],
    icon: Bot,
    accent: 'emerald',
    title: 'Kyi AI',
    subtitle: 'Public AI tool submit form',
    description: 'Submit nhanh với website name, URL và email. Không cần login trước.',
    fields: [
      { name: 'siteName', label: 'Website Name', type: 'text', required: true, placeholder: 'Langflow' },
      { name: 'url', label: 'Website URL', type: 'url', required: true, placeholder: 'https://www.langflow.org' },
      { name: 'contactEmail', label: 'Email', type: 'email', required: true, placeholder: 'hello@example.com' },
    ],
    defaults: { siteName: '', url: '', contactEmail: '' },
  },
  newaiforyou: {
    aliases: ['new_ai_for_you', 'new-ai-for-you'],
    icon: Sparkles,
    accent: 'violet',
    title: 'New AI For You',
    subtitle: 'Google OAuth automation',
    description: 'Worker đăng nhập Google, mở trang submit, điền tool name và URL.',
    fields: [
      { name: 'siteName', label: 'Tool Name', type: 'text', required: true, placeholder: 'Langflow' },
      { name: 'url', label: 'Tool URL', type: 'url', required: true, placeholder: 'https://www.langflow.org' },
    ],
    defaults: { siteName: '', url: '', NewAIForYouDebugHeadful: true },
  },
  awesome_indie: {
    aliases: ['awesomeindie', 'awesome-indie'],
    icon: Rocket,
    accent: 'pink',
    title: 'Awesome Indie',
    subtitle: 'Product submission workflow',
    description: 'Form product đầy đủ: name, URL, tagline, categories, description và social links.',
    fields: [
      { name: 'siteName', label: 'Product Name', type: 'text', required: true, placeholder: 'Langflow' },
      { name: 'url', label: 'Product URL', type: 'url', required: true, placeholder: 'https://www.langflow.org' },
      { name: 'tagline', label: 'Tagline', type: 'text', required: true, placeholder: 'Build LLM workflows visually' },
      { name: 'categories', label: 'Categories', type: 'text', required: true, placeholder: 'AI Tools, Productivity' },
      { name: 'description', label: 'Description', type: 'textarea', required: true, placeholder: 'Describe the product...' },
      { name: 'socialLinks', label: 'Social Links', type: 'textarea', placeholder: 'https://x.com/langflow, https://github.com/langflow-ai/langflow' },
      { name: 'YouTubeVideoUrl', label: 'YouTube Video URL', type: 'url', placeholder: 'https://youtube.com/...' },
    ],
    defaults: { siteName: '', url: '', tagline: '', categories: 'AI Tools, Productivity', description: '', socialLinks: '', YouTubeVideoUrl: '', AwesomeIndieDebugHeadful: true },
  },
  stackshare: {
    aliases: [],
    icon: Layers3,
    accent: 'blue',
    title: 'StackShare',
    subtitle: 'Developer tool automation',
    description: 'Submit tool developer, có hỗ trợ import browser session storage state.',
    fields: [
      { name: 'url', label: 'Website URL', type: 'url', required: true, placeholder: 'https://example.com' },
      { name: 'siteName', label: 'Tool Name', type: 'text', placeholder: 'Optional, worker can crawl it' },
      { name: 'description', label: 'Short Description', type: 'textarea', placeholder: 'Optional description' },
    ],
    defaults: { url: '', siteName: '', description: '' },
    supportsSession: true,
  },
  '10words': {
    aliases: [],
    icon: Code2,
    accent: 'cyan',
    title: '10words',
    subtitle: 'Startup/project listing',
    description: 'Map đúng project name, URL, mô tả, Twitter handle, category và newsletter.',
    fields: [
      { name: 'siteName', label: 'Project Name', type: 'text', required: true, placeholder: 'Langflow' },
      { name: 'url', label: 'Project URL', type: 'url', required: true, placeholder: 'https://www.langflow.org' },
      { name: 'description', label: 'Description', type: 'textarea', required: true, placeholder: 'Build and run LLM workflows visually.' },
      { name: 'twitterHandle', label: 'Twitter Handle', type: 'text', placeholder: '@langflow' },
      { name: 'tenWordsCategory', label: 'Category', type: 'select', options: ['Website', 'SaaS', 'AI', 'Developer Tool', 'Productivity'], required: true },
      { name: 'tenWordsNewsletter', label: 'Newsletter', type: 'select', options: ['No thanks', 'Weekly', 'Daily'] },
    ],
    defaults: { siteName: '', url: '', description: '', twitterHandle: '', tenWordsCategory: 'Website', tenWordsNewsletter: 'No thanks' },
  },
  baitools: {
    aliases: [],
    icon: Bot,
    accent: 'amber',
    title: 'BAI.tools',
    subtitle: 'AI tools directory',
    description: 'Submit tool AI bằng name và website URL, worker xử lý OAuth/automation.',
    fields: [
      { name: 'siteName', label: 'AI Tool Name', type: 'text', required: true, placeholder: 'Langflow' },
      { name: 'url', label: 'Website URL', type: 'url', required: true, placeholder: 'https://www.langflow.org' },
    ],
    defaults: { siteName: '', url: '', BAIToolsUseApi: true, BAIToolsPlanIndex: 0, BAIToolsLocale: 'en' },
  },
  futuretools: {
    aliases: [],
    icon: Compass,
    accent: 'orange',
    title: 'Future Tools',
    subtitle: 'AI tool submission',
    description: 'Form gồm người submit, tool, URL, mô tả, category, pricing và email.',
    fields: [
      { name: 'yourName', label: 'Your Name', type: 'text', required: true, placeholder: 'Nolan' },
      { name: 'siteName', label: 'Tool Name', type: 'text', required: true, placeholder: 'Langflow' },
      { name: 'url', label: 'Tool URL', type: 'url', required: true, placeholder: 'https://www.langflow.org' },
      { name: 'description', label: 'Short Description', type: 'textarea', required: true, placeholder: 'Low-code platform for LLM workflows.' },
      { name: 'category', label: 'Category', type: 'select', options: ['Productivity', 'Marketing', 'Coding', 'Research', 'Design'], required: true },
      { name: 'pricing', label: 'Pricing', type: 'select', options: ['Free', 'Freemium', 'Paid'], required: true },
      { name: 'contactEmail', label: 'Your Email', type: 'email', required: true, placeholder: 'hello@example.com' },
      { name: 'newsletterOptIn', label: 'Join newsletter', type: 'checkbox' },
    ],
    defaults: { yourName: '', siteName: '', url: '', description: '', category: 'Productivity', pricing: 'Free', contactEmail: '', newsletterOptIn: false },
  },
  alternative: {
    aliases: [],
    icon: Wrench,
    accent: 'lime',
    title: 'Alternative',
    subtitle: 'Software submission',
    description: 'Form software chi tiết với category, description, icon, pricing, features và social links.',
    fields: [
      { name: 'siteName', label: 'Software Name', type: 'text', required: true, placeholder: 'Langflow' },
      { name: 'url', label: 'Homepage URL', type: 'url', required: true, placeholder: 'https://www.langflow.org' },
      { name: 'description', label: 'Short Description', type: 'textarea', required: true, placeholder: 'At least 100 characters recommended.' },
      { name: 'fullDescription', label: 'Full Description', type: 'textarea', placeholder: 'Longer software description...' },
      { name: 'iconPath', label: 'Icon Path', type: 'text', required: true, placeholder: '/Users/.../alternative-icon.png' },
      { name: 'category', label: 'Category', type: 'select', options: ['software/web/tools', 'software/web/business', 'software/web/development', 'software/business/marketing', 'software/business/productivity-and-communications'], required: true },
      { name: 'pricingUrl', label: 'Pricing URL', type: 'url', placeholder: 'https://example.com/pricing' },
      { name: 'type', label: 'Type', type: 'select', options: ['online', 'desktop', 'app'] },
      { name: 'monetization', label: 'Monetization', type: 'select', options: ['free', 'freemium', 'paid', 'opensource'] },
      { name: 'status', label: 'Status', type: 'select', options: ['live', 'announced', 'abandoned', 'offline'] },
      { name: 'platforms', label: 'Platforms', type: 'text', placeholder: 'OpenAI, LangChain, Zapier' },
      { name: 'features', label: 'Features', type: 'textarea', placeholder: 'visual builder, automation, API' },
      { name: 'socialLinks', label: 'Social Links', type: 'textarea', placeholder: 'https://x.com/langflow' },
      { name: 'synonyms', label: 'Synonyms', type: 'text', placeholder: 'Lang Flow, Langflow AI' },
    ],
    defaults: {
      siteName: '',
      url: '',
      description: '',
      fullDescription: '',
      iconPath: '/Users/nolanpham/Documents/SEO_Tools/backend/seo-audit-worker/.playwright/alternative-icon.png',
      category: 'software/web/tools',
      pricingUrl: '',
      type: 'online',
      monetization: 'free',
      status: 'live',
      platforms: '',
      features: '',
      socialLinks: '',
      synonyms: '',
    },
  },
  active_search_results: {
    aliases: ['asr'],
    icon: SearchCheck,
    accent: 'green',
    title: 'Active Search Results',
    subtitle: 'Direct HTTP submit',
    description: 'Gửi HTTP request trực tiếp lên directory, phù hợp submit nhanh.',
    fields: [
      { name: 'url', label: 'Website URL', type: 'url', required: true, placeholder: 'https://example.com' },
      { name: 'contactEmail', label: 'Contact Email', type: 'email', required: true, placeholder: 'hello@example.com' },
    ],
    defaults: { url: '', contactEmail: '' },
  },
  default: {
    aliases: [],
    icon: Globe2,
    accent: 'slate',
    title: 'SEO Platform',
    subtitle: 'Generic submit',
    description: 'Submit URL tới platform đã chọn với các field cơ bản.',
    fields: [
      { name: 'url', label: 'Website URL', type: 'url', required: true, placeholder: 'https://example.com' },
      { name: 'siteName', label: 'Site Name', type: 'text', placeholder: 'Example' },
      { name: 'description', label: 'Description', type: 'textarea', placeholder: 'Short website description' },
      { name: 'contactEmail', label: 'Contact Email', type: 'email', placeholder: 'hello@example.com' },
    ],
    defaults: { url: '', siteName: '', description: '', contactEmail: '' },
  },
};

export function normalizePlatformCode(code = '') {
  const normalized = code.toLowerCase().replaceAll('-', '_');
  const exact = PLATFORM_BLUEPRINTS[normalized];
  if (exact) return normalized;

  const match = Object.entries(PLATFORM_BLUEPRINTS).find(([, blueprint]) =>
    blueprint.aliases?.some((alias) => alias.toLowerCase().replaceAll('-', '_') === normalized)
  );

  return match?.[0] ?? normalized;
}

export function getPlatformBlueprint(code) {
  return PLATFORM_BLUEPRINTS[normalizePlatformCode(code)] ?? PLATFORM_BLUEPRINTS.default;
}
