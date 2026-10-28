/**
 * Google Analytics 4 (GA4) Client Dispatcher for JaChai
 * Enables zero-latency event tracking and route change instrumentation.
 */

export const getGAId = (): string => {
  return (
    (typeof process !== 'undefined' &&
      (process.env?.NEXT_PUBLIC_GA_MEASUREMENT_ID || process.env?.NEXT_PUBLIC_GA_ID)) ||
    'G-XNKQ2NC3YG'
  );
};

export const trackGAPageView = (url: string) => {
  if (typeof window !== 'undefined' && (window as any).gtag && getGAId()) {
    (window as any).gtag('config', getGAId(), {
      page_path: url,
    });
  }
};

export const trackGAEvent = (action: string, params?: Record<string, any>) => {
  if (typeof window !== 'undefined' && (window as any).gtag) {
    (window as any).gtag('event', action, params || {});
  }
};

