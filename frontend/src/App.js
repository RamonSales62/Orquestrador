import { useState, useEffect } from "react";
import "@/App.css";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import { Toaster } from "@/components/ui/toaster";
import { 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Shield, 
  User, 
  HardHat,
  Eye,
  Activity,
  TrendingUp,
  AlertTriangle
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EPI_TYPES = {
  helmet: "Capacete",
  safety_glasses: "Óculos de Segurança",
  gloves: "Luvas",
  safety_shoes: "Botas de Segurança",
  vest: "Colete",
  mask: "Máscara"
};

function App() {
  const [stats, setStats] = useState(null);
  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  // Form state for event simulator
  const [faceDetected, setFaceDetected] = useState(true);
  const [faceConfidence, setFaceConfidence] = useState(0.95);
  const [faceQuality, setFaceQuality] = useState(0.90);
  const [personId, setPersonId] = useState("");
  const [location, setLocation] = useState("Entrada Principal");
  
  const [selectedEpis, setSelectedEpis] = useState([
    { type: "helmet", detected: true, confidence: 0.92, properly_worn: true }
  ]);

  useEffect(() => {
    fetchStats();
    fetchDecisions();
    const interval = setInterval(() => {
      fetchStats();
      fetchDecisions();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error("Erro ao buscar estatísticas:", error);
    }
  };

  const fetchDecisions = async () => {
    try {
      const response = await axios.get(`${API}/decisions?limit=10`);
      setDecisions(response.data);
    } catch (error) {
      console.error("Erro ao buscar decisões:", error);
    }
  };

  const handleOrchestrate = async () => {
    setLoading(true);
    try {
      const payload = {
        face_event: {
          detected: faceDetected,
          confidence: parseFloat(faceConfidence),
          quality_score: parseFloat(faceQuality),
          person_id: personId || null,
          location: location
        },
        epi_events: selectedEpis.map(epi => ({
          epi_type: epi.type,
          detected: epi.detected,
          confidence: parseFloat(epi.confidence),
          properly_worn: epi.properly_worn,
          person_id: personId || null,
          location: location
        })),
        person_id: personId || null,
        location: location,
        required_epis: ["helmet"]
      };

      const response = await axios.post(`${API}/orchestrate`, payload);
      
      toast({
        title: response.data.decision === "approved" ? "✅ Acesso Aprovado" : "❌ Acesso Negado",
        description: response.data.reason,
        variant: response.data.decision === "approved" ? "default" : "destructive"
      });

      await fetchStats();
      await fetchDecisions();
    } catch (error) {
      toast({
        title: "Erro",
        description: "Erro ao processar orquestração",
        variant: "destructive"
      });
      console.error("Erro:", error);
    } finally {
      setLoading(false);
    }
  };

  const addEpi = () => {
    setSelectedEpis([
      ...selectedEpis,
      { type: "safety_glasses", detected: true, confidence: 0.85, properly_worn: true }
    ]);
  };

  const removeEpi = (index) => {
    setSelectedEpis(selectedEpis.filter((_, i) => i !== index));
  };

  const updateEpi = (index, field, value) => {
    const updated = [...selectedEpis];
    updated[index][field] = value;
    setSelectedEpis(updated);
  };

  const getDecisionIcon = (decision) => {
    switch(decision) {
      case "approved": return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case "rejected": return <XCircle className="h-5 w-5 text-red-500" />;
      default: return <Clock className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getDecisionBadge = (decision) => {
    const variants = {
      approved: "default",
      rejected: "destructive",
      pending: "secondary"
    };
    const labels = {
      approved: "Aprovado",
      rejected: "Rejeitado",
      pending: "Pendente"
    };
    return <Badge variant={variants[decision]}>{labels[decision]}</Badge>;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <Toaster />
      
      {/* Header */}
      <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700 shadow-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                  EPI Orchestrator
                </h1>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Sistema de Orquestração de Segurança
                </p>
              </div>
            </div>
            <Badge variant="outline" className="text-green-600 border-green-600">
              <Activity className="h-3 w-3 mr-1" />
              Operacional
            </Badge>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        
        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Total de Decisões</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_decisions}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  {stats.total_face_events} eventos faciais
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Aprovados</CardTitle>
                <CheckCircle2 className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{stats.approved_decisions}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  {stats.total_decisions > 0 
                    ? `${((stats.approved_decisions / stats.total_decisions) * 100).toFixed(1)}% de aprovação`
                    : "0% de aprovação"
                  }
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Rejeitados</CardTitle>
                <XCircle className="h-4 w-4 text-red-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">{stats.rejected_decisions}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  {stats.total_decisions > 0 
                    ? `${((stats.rejected_decisions / stats.total_decisions) * 100).toFixed(1)}% de rejeição`
                    : "0% de rejeição"
                  }
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Eventos EPI</CardTitle>
                <HardHat className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_epi_events}</div>
                <p className="text-xs text-muted-foreground mt-1">
                  Detecções de equipamentos
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        <Tabs defaultValue="simulator" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 lg:w-[400px]">
            <TabsTrigger value="simulator">
              <Shield className="h-4 w-4 mr-2" />
              Simulador
            </TabsTrigger>
            <TabsTrigger value="history">
              <Activity className="h-4 w-4 mr-2" />
              Histórico
            </TabsTrigger>
          </TabsList>

          {/* Event Simulator Tab */}
          <TabsContent value="simulator" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Eye className="h-5 w-5" />
                  Simulador de Eventos
                </CardTitle>
                <CardDescription>
                  Simule eventos de detecção facial e EPI para testar o orquestrador
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                
                {/* Informações Gerais */}
                <div className="space-y-4">
                  <h3 className="font-semibold flex items-center gap-2">
                    <User className="h-4 w-4" />
                    Informações Gerais
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="personId">ID da Pessoa (opcional)</Label>
                      <Input
                        id="personId"
                        placeholder="Ex: FUNC-001"
                        value={personId}
                        onChange={(e) => setPersonId(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="location">Local</Label>
                      <Input
                        id="location"
                        placeholder="Ex: Entrada Principal"
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                      />
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Detecção Facial */}
                <div className="space-y-4">
                  <h3 className="font-semibold flex items-center gap-2">
                    <Eye className="h-4 w-4" />
                    Detecção Facial
                  </h3>
                  
                  <div className="flex items-center gap-4">
                    <Label htmlFor="faceDetected" className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        id="faceDetected"
                        checked={faceDetected}
                        onChange={(e) => setFaceDetected(e.target.checked)}
                        className="w-4 h-4"
                      />
                      Face Detectada
                    </Label>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="faceConfidence">
                        Confiança: {(faceConfidence * 100).toFixed(0)}%
                      </Label>
                      <Input
                        id="faceConfidence"
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={faceConfidence}
                        onChange={(e) => setFaceConfidence(e.target.value)}
                        className="cursor-pointer"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="faceQuality">
                        Qualidade: {(faceQuality * 100).toFixed(0)}%
                      </Label>
                      <Input
                        id="faceQuality"
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={faceQuality}
                        onChange={(e) => setFaceQuality(e.target.value)}
                        className="cursor-pointer"
                      />
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Detecção de EPIs */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold flex items-center gap-2">
                      <HardHat className="h-4 w-4" />
                      Equipamentos de Proteção (EPIs)
                    </h3>
                    <Button onClick={addEpi} size="sm" variant="outline">
                      + Adicionar EPI
                    </Button>
                  </div>

                  {selectedEpis.map((epi, index) => (
                    <Card key={index} className="bg-slate-50 dark:bg-slate-800">
                      <CardContent className="pt-6 space-y-4">
                        <div className="flex items-center justify-between">
                          <Select
                            value={epi.type}
                            onValueChange={(value) => updateEpi(index, 'type', value)}
                          >
                            <SelectTrigger className="w-[200px]">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {Object.entries(EPI_TYPES).map(([key, label]) => (
                                <SelectItem key={key} value={key}>
                                  {label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <Button
                            onClick={() => removeEpi(index)}
                            variant="ghost"
                            size="sm"
                            className="text-red-500"
                          >
                            Remover
                          </Button>
                        </div>

                        <div className="flex items-center gap-4">
                          <Label className="flex items-center gap-2 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={epi.detected}
                              onChange={(e) => updateEpi(index, 'detected', e.target.checked)}
                              className="w-4 h-4"
                            />
                            Detectado
                          </Label>
                          <Label className="flex items-center gap-2 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={epi.properly_worn}
                              onChange={(e) => updateEpi(index, 'properly_worn', e.target.checked)}
                              className="w-4 h-4"
                            />
                            Usado Corretamente
                          </Label>
                        </div>

                        <div className="space-y-2">
                          <Label>
                            Confiança: {(epi.confidence * 100).toFixed(0)}%
                          </Label>
                          <Input
                            type="range"
                            min="0"
                            max="1"
                            step="0.01"
                            value={epi.confidence}
                            onChange={(e) => updateEpi(index, 'confidence', parseFloat(e.target.value))}
                            className="cursor-pointer"
                          />
                        </div>
                      </CardContent>
                    </Card>
                  ))}

                  {selectedEpis.length === 0 && (
                    <Alert>
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>
                        Adicione pelo menos um EPI para processar a orquestração
                      </AlertDescription>
                    </Alert>
                  )}
                </div>

                <Separator />

                <Button 
                  onClick={handleOrchestrate} 
                  disabled={loading || selectedEpis.length === 0}
                  className="w-full"
                  size="lg"
                >
                  {loading ? "Processando..." : "Processar Orquestração"}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Histórico de Decisões</CardTitle>
                <CardDescription>
                  Últimas decisões tomadas pelo orquestrador
                </CardDescription>
              </CardHeader>
              <CardContent>
                {decisions.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    Nenhuma decisão registrada ainda
                  </div>
                ) : (
                  <div className="space-y-4">
                    {decisions.map((decision) => (
                      <Card key={decision.id} className="bg-slate-50 dark:bg-slate-800">
                        <CardContent className="pt-6">
                          <div className="flex items-start justify-between">
                            <div className="space-y-2 flex-1">
                              <div className="flex items-center gap-2">
                                {getDecisionIcon(decision.decision)}
                                {getDecisionBadge(decision.decision)}
                                {decision.person_id && (
                                  <Badge variant="outline">{decision.person_id}</Badge>
                                )}
                                {decision.location && (
                                  <Badge variant="outline">{decision.location}</Badge>
                                )}
                              </div>
                              <p className="text-sm text-muted-foreground">
                                {decision.reason}
                              </p>
                              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                                <span>
                                  Confiança: {(decision.confidence_score * 100).toFixed(0)}%
                                </span>
                                <span>
                                  {new Date(decision.timestamp).toLocaleString('pt-BR')}
                                </span>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>

      <footer className="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-700 mt-12">
        <div className="container mx-auto px-6 py-4">
          <p className="text-center text-sm text-muted-foreground">
            EPI Orchestrator v1.0.0 - Sistema de Orquestração de Segurança
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
