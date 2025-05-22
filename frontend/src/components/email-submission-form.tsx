"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "sonner";
import { UploadCloud, Loader2, File, X } from "lucide-react";
import { API_URLS } from "@/lib/api-helpers";

export default function EmailSubmissionForm() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
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

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleCheckboxChange = (name: string, checked: boolean) => {
    setFormData((prev) => ({ ...prev, [name]: checked }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
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
    setLoading(true);

    try {
      // Validações básicas
      if (inputMethod === "text" && !formData.content) {
        toast.error("O conteúdo do email é obrigatório");
        setLoading(false);
        return;
      }

      if (inputMethod === "file" && !formData.file) {
        toast.error("Selecione um arquivo para upload");
        setLoading(false);
        return;
      }

      const data = new FormData();
      data.append("sender", formData.sender);
      data.append("subject", formData.subject);
      data.append("content", formData.content);
      data.append("input_method", inputMethod);
      data.append("use_file_subject", formData.use_file_subject ? "true" : "false");
      data.append("use_file_sender", formData.use_file_sender ? "true" : "false");

      if (formData.file) {
        data.append("file", formData.file);
      }

      toast.info("Enviando dados para classificação...");

      // Usar o novo endpoint da API que não requer CSRF
      console.log("Enviando para:", API_URLS.SUBMIT_EMAIL);
      const response = await fetch(API_URLS.SUBMIT_EMAIL, {
        method: "POST",
        body: data,
      });

      if (!response.ok) {
        // Handle schema-related errors
        const errorText = await response.text();
        console.error("Resposta de erro:", errorText);

        if (errorText.includes("has no column named")) {
          throw new Error("Erro de esquema do banco de dados. Execute as migrações do backend.");
        } else {
          // Try to parse as JSON if possible
          try {
            const errorData = JSON.parse(errorText);
            throw new Error(errorData.message || `Erro ${response.status}: ${response.statusText || 'Erro ao processar a requisição'}`);
          } catch {
            throw new Error(`Erro ${response.status}: ${response.statusText || 'Erro ao processar a requisição'}`);
          }
        }
      }

      const result = await response.json();
      console.log("Resposta recebida:", result);

      if (result.id) {
        toast.success("Email classificado com sucesso!", {
          description: `Classificação: ${result.category === "productive" ? "Produtivo" : "Improdutivo"}`,
        });
        router.push(`/emails/${result.id}`);
      } else if (result.status === 'error') {
        throw new Error(result.message || "Erro no servidor");
      } else {
        throw new Error("ID do email não recebido na resposta");
      }
    } catch (error) {
      console.error("Erro ao enviar o email:", error);

      // Special message for migration errors
      if (error instanceof Error && error.message.includes("migrações")) {
        toast.error("Erro de configuração do servidor", {
          description: error.message,
        });
      } else {
        toast.error("Erro ao enviar o email", {
          description: error instanceof Error ? error.message : "Ocorreu um erro desconhecido",
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  return (
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
          <Label htmlFor="sender">Remetente</Label>
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
          <Label htmlFor="subject">Assunto</Label>
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
            <Label htmlFor="content">Conteúdo</Label>
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

      <Button type="submit" className="w-full" disabled={loading}>
        {loading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Processando...
          </>
        ) : (
          "Classificar Email"
        )}
      </Button>
    </form>
  );
}
