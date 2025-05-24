import { Metadata } from "next";
import { Shield, Lock, Users, Zap, Database, Globe } from "lucide-react";

export const metadata: Metadata = {
  title: "Sobre | Classificador de Emails",
  description: "Informações sobre o projeto de classificação de emails",
};

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-[#0A0A0A] transition-colors duration-300">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4 text-gray-900 dark:text-white">
              Sobre o Email Classifier
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300">
              Sistema inteligente de classificação de emails com foco em privacidade e eficiência
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2">
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm dark:shadow-gray-900/50">
              <div className="flex items-center gap-3 mb-4">
                <Shield className="h-8 w-8 text-green-500 dark:text-green-400" />
                <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
                  Privacidade Garantida
                </h2>
              </div>
              <div className="space-y-3">
                <p className="text-base text-gray-600 dark:text-gray-300">
                  Cada usuário vê apenas seus próprios emails classificados através de isolamento automático por IP.
                </p>
                <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-2">
                  <li className="flex items-center gap-2">
                    <Lock className="h-4 w-4 text-green-500 dark:text-green-400" />
                    Zero compartilhamento entre usuários
                  </li>
                  <li className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-green-500 dark:text-green-400" />
                    Funciona sem necessidade de login
                  </li>
                  <li className="flex items-center gap-2">
                    <Database className="h-4 w-4 text-green-500 dark:text-green-400" />
                    Dados isolados automaticamente
                  </li>
                </ul>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm dark:shadow-gray-900/50">
              <div className="flex items-center gap-3 mb-4">
                <Zap className="h-8 w-8 text-blue-500 dark:text-blue-400" />
                <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
                  Como Funciona
                </h2>
              </div>
              <div className="space-y-3">
                <p className="text-base text-gray-600 dark:text-gray-300">
                  O sistema analisa o conteúdo do email usando IA avançada para determinar se requer ação imediata (produtivo) ou se é informativo (improdutivo).
                </p>
                <p className="text-base text-gray-600 dark:text-gray-300">
                  A classificação é feita através de uma combinação de heurísticas e modelos de linguagem avançados da Google Gemini API.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm dark:shadow-gray-900/50 mt-8">
            <div className="flex items-center gap-3 mb-6">
              <Globe className="h-8 w-8 text-purple-500 dark:text-purple-400" />
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
                Tecnologias Utilizadas
              </h2>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <h3 className="font-medium mb-2 text-gray-900 dark:text-white">Frontend</h3>
                <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-1">
                  <li>• Next.js 14 (React)</li>
                  <li>• TypeScript</li>
                  <li>• TailwindCSS + shadcn/ui</li>
                  <li>• Vercel (Deploy)</li>
                </ul>
              </div>
              <div>
                <h3 className="font-medium mb-2 text-gray-900 dark:text-white">Backend</h3>
                <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-1">
                  <li>• Django (Python)</li>
                  <li>• Google Gemini 1.5 Flash</li>
                  <li>• PostgreSQL + SQLite</li>
                  <li>• Railway (Deploy)</li>
                </ul>
              </div>
              <div>
                <h3 className="font-medium mb-2 text-gray-900 dark:text-white">Recursos</h3>
                <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-1">
                  <li>• Rate Limiting inteligente</li>
                  <li>• Sistema de filas assíncronas</li>
                  <li>• Processamento de PDF/TXT</li>
                  <li>• API RESTful completa</li>
                </ul>
              </div>
              <div>
                <h3 className="font-medium mb-2 text-gray-900 dark:text-white">Segurança</h3>
                <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-1">
                  <li>• Isolamento por IP</li>
                  <li>• Headers CORS seguros</li>
                  <li>• Validação de entrada</li>
                  <li>• Monitoramento de uso</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/30 dark:to-purple-950/30 rounded-lg border border-blue-200 dark:border-blue-800/50 p-6 mt-8">
            <h2 className="text-2xl font-semibold mb-4 text-gray-900 dark:text-white">
              Sobre o Projeto
            </h2>
            <p className="text-base text-gray-700 dark:text-gray-300 mb-4">
              Este projeto foi desenvolvido como demonstração de competências técnicas,
              integrando conceitos modernos de desenvolvimento web, inteligência artificial
              e boas práticas de segurança.
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Desenvolvido por{" "}
              <a
                href="https://github.com/jonhvmp"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 dark:text-blue-400 hover:underline font-medium transition-colors"
              >
                João Alex
              </a>
              {" "}• Código disponível no{" "}
              <a
                href="https://github.com/jonhvmp/email_classifier"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 dark:text-blue-400 hover:underline font-medium transition-colors"
              >
                GitHub
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
