"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { UploadCloud, Loader2, File, X, Clock, AlertTriangle } from "lucide-react";
import { submitEmailAndWait, JobStatus } from "@/lib/api-helpers";
import { QueueStatusDialog } from "./queue-status-dialog";

const CHAR_LIMITS = {
  sender: 50,
  subject: 200,
  content: 5000,
};

export default function EmailSubmissionForm() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [processingStatus, setProcessingStatus] = useState<{
    status?: string;
    message?: string;
    progress: number;
    jobId?: string;
    position?: number;
    waitTime?: number;
  } | null>(null);
  const [inputMethod, setInputMethod] = useState("text");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [formData, setFormData] = useState({
    sender: "",
    subject: "",
    content: "",
    file: null as File | null,
    use_file_subject: true,
    use_file_sender: true,
  });

  // Estados para controle de limites de caracteres
  const [charCounts, setCharCounts] = useState({
    sender: 0,
    subject: 0,
    content: 0,
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;

    // Verificar limite de caracteres
    const limit = CHAR_LIMITS[name as keyof typeof CHAR_LIMITS];
    if (limit && value.length > limit) {
      toast.error(`Campo ${name === 'sender' ? 'remetente' : name === 'subject' ? 'assunto' : 'conteúdo'} excede o limite`, {
        description: `Máximo de ${limit} caracteres permitidos`
      });
      return;
    }

    setFormData((prev) => ({ ...prev, [name]: value }));

    // Atualizar contagem de caracteres
    if (limit) {
      setCharCounts((prev) => ({ ...prev, [name]: value.length }));
    }
  };

  const handleCheckboxChange = (name: string, checked: boolean) => {
    setFormData((prev) => ({ ...prev, [name]: checked }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];

      // Verificar extensão do arquivo
      const allowedExtensions = ['.txt', '.pdf'];
      const fileExt = file.name.split('.').pop()?.toLowerCase();

      if (!fileExt || !allowedExtensions.includes(`.${fileExt}`)) {
        toast.error("Tipo de arquivo não permitido", {
          description: "Apenas arquivos .txt ou .pdf são aceitos"
        });
        return;
      }

      setFormData((prev) => ({ ...prev, file }));
      toast.info(`Arquivo selecionado: ${file.name}`, {
        description: `Tamanho: ${(file.size / 1024).toFixed(2)} KB`
      });
    }
  };

  const removeFile = () => {
    setFormData((prev) => ({ ...prev, file: null }));
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      // Validações básicas
      if (inputMethod === "text" && !formData.content) {
        toast.error("O conteúdo do email é obrigatório");
        return;
      }

      if (inputMethod === "file" && !formData.file) {
        toast.error("Selecione um arquivo para upload");
        return;
      }

      // Validar campos quando as caixas de seleção estiverem marcadas
      if (formData.use_file_subject && !formData.subject.trim()) {
        toast.error("Preencha o campo de assunto ou desmarque a opção correspondente");
        return;
      }

      if (formData.use_file_sender && !formData.sender.trim()) {
        toast.error("Preencha o campo de remetente ou desmarque a opção correspondente");
        return;
      }

      setLoading(true);
      setProcessingStatus({
        status: "iniciando",
        message: "Preparando para envio...",
        progress: 5
      });

      const data = new FormData();

      // Só adiciona os campos se forem preenchidos ou se as opções estiverem marcadas
      if (formData.sender) {
        data.append("sender", formData.sender);
      }

      if (formData.subject) {
        data.append("subject", formData.subject);
      }

      data.append("content", formData.content);
      data.append("input_method", inputMethod);
      data.append("use_file_subject", formData.use_file_subject ? "true" : "false");
      data.append("use_file_sender", formData.use_file_sender ? "true" : "false");

      if (formData.file) {
        // Verificar extensão do arquivo
        const allowedExtensions = ['.txt', '.pdf'];
        const fileExt = formData.file.name.split('.').pop()?.toLowerCase();

        if (!fileExt || !allowedExtensions.includes(`.${fileExt}`)) {
          toast.error("Tipo de arquivo não permitido", {
            description: "Apenas arquivos .txt ou .pdf são aceitos"
          });
          setLoading(false);
          setProcessingStatus(null);
          return;
        }

        data.append("file", formData.file);
      }

      setProcessingStatus({
        status: "enviando",
        message: "Enviando dados para classificação...",
        progress: 10
      });

      // Usar nossa função avançada de submit com monitoramento
      await submitEmailAndWait(data, {
        // Callback para atualizações de status do job
        onUpdate: (jobStatus: JobStatus) => {
          switch (jobStatus.status) {
            case 'queued':
              setProcessingStatus(prev => ({
                ...prev!,
                status: "enfileirado",
                message: "Na fila de processamento...",
                progress: Math.min(30, 10 + jobStatus.position_in_queue * 2),
                jobId: jobStatus.id
              }));
              break;
            case 'processing':
              setProcessingStatus(prev => ({
                ...prev!,
                status: "processando",
                message: "Classificando email com IA...",
                progress: 60,
                jobId: jobStatus.id
              }));
              break;
            case 'completed':
              // Verificar se o email está processado (novo campo)
              if (jobStatus.email && jobStatus.email.is_processed) {
                setProcessingStatus(prev => ({
                  ...prev!,
                  status: "concluído",
                  message: `Email classificado como ${jobStatus.email?.category === 'productive' ? 'produtivo' : 'improdutivo'}!`,
                  progress: 100,
                  jobId: jobStatus.id
                }));
              } else {
                setProcessingStatus(prev => ({
                  ...prev!,
                  status: "finalizando",
                  message: "Finalizando processamento...",
                  progress: 80,
                  jobId: jobStatus.id
                }));
              }
              break;
            case 'failed':
              throw new Error(jobStatus.error_message || "Falha no processamento");
            case 'expired':
              throw new Error("Tempo limite de processamento excedido");
          }
        },
        // Callback para atualizações sobre a fila
        onQueueUpdate: ({ position, waitTime }) => {
          setProcessingStatus(prev => ({
            ...prev!,
            position,
            waitTime,
            message: `Na fila: posição ${position}`,
          }));
        },
        // Configurações
        maxAttempts: 120, // 2 minutos
        interval: 1000 // 1 segundo
      }).then(result => {
        // Sucesso - redirecionar para página de detalhes
        if (result && result.id) {
          handleSuccess(result.id);
        } else if (result && result.emailId) {
          // Suporte ao formato de retorno atualizado
          handleSuccess(result.emailId);
        } else {
          throw new Error("Resposta incompleta do servidor");
        }
      }).catch(error => {
        // Erro no processamento
        handleError(error);
      });

    } catch (error) {
      console.error("Erro ao processar o email:", error);
      handleError(error);
    }
  };

  const handleSuccess = (emailId: number) => {
    toast.success("Email classificado com sucesso!", {
      description: "Redirecionando para a página de detalhes...",
    });

    setLoading(false);
    setProcessingStatus(null);

    // Navegar para a página de detalhes do email
    router.push(`/emails/${emailId}`);
  };

  const handleError = (error: unknown) => {
    toast.error("Erro ao processar o email", {
      description: error instanceof Error ? error.message : "Ocorreu um erro desconhecido",
    });
    setLoading(false);
    setProcessingStatus(null);
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const getCharCountColor = (field: keyof typeof CHAR_LIMITS) => {
    const count = charCounts[field];
    const limit = CHAR_LIMITS[field];
    const percentage = (count / limit) * 100;

    if (percentage >= 100) return "text-red-500";
    if (percentage >= 80) return "text-amber-500";
    return "text-muted-foreground";
  };

  const isNearLimit = (field: keyof typeof CHAR_LIMITS) => {
    const count = charCounts[field];
    const limit = CHAR_LIMITS[field];
    return (count / limit) >= 0.8;
  };

  return (
    <>
      <div className="flex justify-end mb-4">
        <QueueStatusDialog />
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-4">
          <div>
            <Label>Método de entrada</Label>
            <RadioGroup
              value={inputMethod}
              onValueChange={setInputMethod}
              className="flex flex-col space-y-1 mt-2"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="text" id="text" />
                <Label htmlFor="text" className="font-normal">Texto direto</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="file" id="file" />
                <Label htmlFor="file" className="font-normal">Upload de arquivo</Label>
              </div>
            </RadioGroup>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <Label htmlFor="sender">Remetente</Label>
              <div className="flex items-center gap-1">
                {isNearLimit('sender') && (
                  <AlertTriangle className="h-3 w-3 text-amber-500" />
                )}
                <span className={`text-xs ${getCharCountColor('sender')}`}>
                  {charCounts.sender}/{CHAR_LIMITS.sender}
                </span>
              </div>
            </div>
            <Input
              id="sender"
              name="sender"
              type="email"
              placeholder="email@exemplo.com"
              value={formData.sender}
              onChange={handleInputChange}
              className="mt-1"
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <Label htmlFor="subject">Assunto</Label>
              <div className="flex items-center gap-1">
                {isNearLimit('subject') && (
                  <AlertTriangle className="h-3 w-3 text-amber-500" />
                )}
                <span className={`text-xs ${getCharCountColor('subject')}`}>
                  {charCounts.subject}/{CHAR_LIMITS.subject}
                </span>
              </div>
            </div>
            <Input
              id="subject"
              name="subject"
              placeholder="Assunto do email"
              value={formData.subject}
              onChange={handleInputChange}
              className="mt-1"
            />
          </div>

          {inputMethod === "text" ? (
            <div>
              <div className="flex justify-between items-center mb-1">
                <Label htmlFor="content">Conteúdo</Label>
                <div className="flex items-center gap-1">
                  {isNearLimit('content') && (
                    <AlertTriangle className="h-3 w-3 text-amber-500" />
                  )}
                  <span className={`text-xs ${getCharCountColor('content')}`}>
                    {charCounts.content}/{CHAR_LIMITS.content}
                  </span>
                </div>
              </div>
              <Textarea
                id="content"
                name="content"
                placeholder="Digite o conteúdo do email aqui..."
                value={formData.content}
                onChange={handleInputChange}
                className="mt-1"
                rows={6}
              />
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <Label htmlFor="file-input">Arquivo (.txt, .pdf)</Label>
                <div className="mt-1 border-2 border-dashed border-muted rounded-md p-4">
                  <Input
                    id="file-input"
                    ref={fileInputRef}
                    type="file"
                    accept=".txt,.pdf"
                    onChange={handleFileChange}
                    className="hidden"
                  />

                  {formData.file ? (
                    <div className="flex items-center justify-between p-2 bg-muted/50 rounded">
                      <div className="flex items-center space-x-2">
                        <File className="h-5 w-5 text-blue-500" />
                        <span className="text-sm">{formData.file.name}</span>
                      </div>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={removeFile}
                        className="h-8 w-8 p-0"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={triggerFileInput}
                      className="w-full cursor-pointer flex flex-col items-center justify-center space-y-2 p-4 hover:bg-muted/50 rounded-md transition-colors"
                    >
                      <UploadCloud className="h-10 w-10 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">
                        Clique para selecionar um arquivo
                      </span>
                    </button>
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="use_file_subject"
                  checked={formData.use_file_subject}
                  onCheckedChange={(checked) => handleCheckboxChange("use_file_subject", !!checked)}
                />
                <Label htmlFor="use_file_subject" className="font-normal text-sm">
                  Usar campo de assunto acima (ignorar assunto do arquivo)
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="use_file_sender"
                  checked={formData.use_file_sender}
                  onCheckedChange={(checked) => handleCheckboxChange("use_file_sender", !!checked)}
                />
                <Label htmlFor="use_file_sender" className="font-normal text-sm">
                  Usar campo de remetente acima (ignorar remetente do arquivo)
                </Label>
              </div>
            </div>
          )}
        </div>

        {processingStatus && (
          <div className="space-y-2 bg-muted/30 p-3 rounded-md">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">{processingStatus.message}</span>
              <span className="text-xs text-muted-foreground">
                {processingStatus.status === "enfileirado" && processingStatus.waitTime &&
                  `Espera estimada: ~${processingStatus.waitTime}s`}
              </span>
            </div>
            <Progress value={processingStatus.progress} className="h-2" />

            {processingStatus.status === "enfileirado" && (
              <div className="flex items-center text-xs text-muted-foreground mt-1">
                <Clock className="h-3 w-3 mr-1" />
                <span>Posição na fila: {processingStatus.position || "..."}</span>
              </div>
            )}
          </div>
        )}

        <Button
          type="submit"
          className="w-full"
          disabled={loading}>
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              {processingStatus?.status || "Processando..."}
            </>
          ) : (
            "Classificar Email"
          )}
        </Button>
      </form>
    </>
  );
}
