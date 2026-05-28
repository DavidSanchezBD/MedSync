from pydantic import BaseModel, EmailStr, Field


class RegistroRequest(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class PerfilRequest(BaseModel):
    idade: int = Field(ge=1, le=120)
    genero_biologico: str = Field(min_length=2, max_length=30)
    peso_kg: float = Field(gt=0, le=500)
    altura_cm: float = Field(gt=0, le=300)
    condicoes_previas: str | None = None
    historico_familiar: str | None = None
