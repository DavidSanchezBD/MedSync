import uuid

from database.db import obter_conexao


def salvar_perfil(usuario_id: str, dados: dict) -> dict:
    with obter_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM perfis_saude WHERE usuario_id = %s", (usuario_id,)
            )
            existente = cur.fetchone()

            if existente:
                cur.execute(
                    """
                    UPDATE perfis_saude
                    SET idade = %s, genero_biologico = %s, peso_kg = %s,
                        altura_cm = %s, condicoes_previas = %s, historico_familiar = %s
                    WHERE usuario_id = %s
                    """,
                    (
                        dados.get("idade"),
                        dados.get("genero_biologico"),
                        dados.get("peso_kg"),
                        dados.get("altura_cm"),
                        dados.get("condicoes_previas"),
                        dados.get("historico_familiar"),
                        usuario_id,
                    ),
                )
            else:
                perfil_id = str(uuid.uuid4())
                cur.execute(
                    """
                    INSERT INTO perfis_saude
                        (id, usuario_id, idade, genero_biologico, peso_kg,
                         altura_cm, condicoes_previas, historico_familiar)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        perfil_id,
                        usuario_id,
                        dados.get("idade"),
                        dados.get("genero_biologico"),
                        dados.get("peso_kg"),
                        dados.get("altura_cm"),
                        dados.get("condicoes_previas"),
                        dados.get("historico_familiar"),
                    ),
                )

    return {"mensagem": "Perfil salvo com sucesso."}
