"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("[JaChai Portal Caught Exception]:", error, errorInfo);
    this.setState({ errorInfo });
  }

  handleReload = () => {
    if (typeof window !== "undefined") {
      window.location.reload();
    }
  };

  handleResetAndReload = () => {
    if (typeof window !== "undefined") {
      try {
        sessionStorage.clear();
        localStorage.removeItem("jc_pin_fails");
        localStorage.removeItem("jc_lockout_until");
      } catch (e) {
        console.warn("Storage reset error:", e);
      }
      window.location.href = "/";
    }
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-[#0A0B0E] text-white flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-[#12141C] border border-white/10 rounded-2xl p-6 shadow-2xl text-center space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center justify-center mx-auto text-2xl font-bold">
              !
            </div>
            <div>
              <h2 className="text-lg font-bold text-white uppercase tracking-wider font-display">
                Portal Re-synchronizing
              </h2>
              <p className="text-xs text-white/60 mt-1 leading-relaxed">
                JaChai encountered a temporary client-side interface mismatch. Click below to refresh the live pricing index.
              </p>
            </div>

            {this.state.error && (
              <div className="text-left bg-black/40 border border-white/5 rounded-xl p-3 font-mono text-[11px] text-rose-300 break-words max-h-28 overflow-y-auto">
                {this.state.error.message || String(this.state.error)}
              </div>
            )}

            <div className="flex flex-col sm:flex-row gap-2 pt-2">
              <button
                type="button"
                onClick={this.handleReload}
                className="flex-1 py-2.5 px-4 rounded-xl bg-[#0F766E] hover:bg-[#14B8A6] text-white font-extrabold text-xs uppercase tracking-wider transition cursor-pointer"
              >
                Reload JaChai
              </button>
              <button
                type="button"
                onClick={this.handleResetAndReload}
                className="py-2.5 px-4 rounded-xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs uppercase tracking-wider transition cursor-pointer"
              >
                Clear Cache & Restart
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
