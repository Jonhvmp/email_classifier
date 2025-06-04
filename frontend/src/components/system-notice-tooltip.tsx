"use client";

import { useState, createContext, useContext } from "react";
import { Info, X, ExternalLink } from "lucide-react";

const SystemStatusContext = createContext({ isSystemDisabled: true });

export function useSystemStatus() {
  return useContext(SystemStatusContext);
}

interface SystemNoticeTooltipProps {
  children?: React.ReactNode;
}

export function SystemNoticeTooltip({ children }: SystemNoticeTooltipProps) {
  const [isVisible, setIsVisible] = useState(true);

  return (
    <SystemStatusContext.Provider value={{ isSystemDisabled: true }}>
      {isVisible && (
        <div className="fixed top-20 right-4 z-50 max-w-sm">
          <div className="bg-amber-50 dark:bg-amber-950/90 border border-amber-200 dark:border-amber-800 rounded-lg p-4 shadow-lg">
            <div className="flex items-start gap-3">
              <Info className="h-5 w-5 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-semibold text-amber-800 dark:text-amber-200 mb-2">
                  ⚠️ Sistema Temporariamente Indisponível
                </h3>
                <div className="text-xs text-amber-700 dark:text-amber-300 space-y-2">
                  <p>
                    O backend foi desabilitado devido aos custos operacionais.
                    Apenas o frontend está disponível para demonstração.
                  </p>
                  <p>
                    Este projeto foi desenvolvido para um case de{" "}
                    <strong>Engenheiro de Software Jr</strong>.
                  </p>
                  <div className="pt-2 border-t border-amber-200 dark:border-amber-700">
                    <p className="font-medium mb-1">Contato para mais informações:</p>
                    <div className="space-y-1">
                      <a
                        href="https://www.linkedin.com/in/jonhvmp"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-amber-600 dark:text-amber-400 hover:text-amber-800 dark:hover:text-amber-200 transition-colors"
                      >
                        <ExternalLink className="h-3 w-3" />
                        LinkedIn
                      </a>
                      <a
                        href="https://github.com/jonhvmp"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-amber-600 dark:text-amber-400 hover:text-amber-800 dark:hover:text-amber-200 transition-colors"
                      >
                        <ExternalLink className="h-3 w-3" />
                        GitHub
                      </a>
                    </div>
                  </div>
                </div>
              </div>
              <button
                onClick={() => setIsVisible(false)}
                className="text-amber-500 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-200 transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}
      {children}
    </SystemStatusContext.Provider>
  );
}
