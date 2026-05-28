from database.db import obter_conexao


def buscar_perfil(usuario_id: str) -> dict | None:
    with obter_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT idade, genero_biologico, peso_kg, altura_cm,
                       condicoes_previas, historico_familiar
                FROM perfis_saude
                WHERE usuario_id = %s
                ORDER BY id DESC
                LIMIT 1
                """,
                (usuario_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None


def salvar_perfil(usuario_id: str, dados) -> dict:
    estilo_vida = f"IMC contextual — peso {dados.peso_kg}kg, altura {dados.altura_cm}cm"
    with obter_conexao() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM perfis_saude WHERE usuario_id = %s", (usuario_id,))
            try:
                cur.execute(
                    """
                    INSERT INTO perfis_saude (
                        usuario_id, idade, genero_biologico, peso_kg, altura_cm,
                        condicoes_previas, historico_familiar, estilo_vida
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING idade, genero_biologico, peso_kg, altura_cm,
                              condicoes_previas, historico_familiar
                    """,
                    (
                        usuario_id,
                        dados.idade,
                        dados.genero_biologico,
                        dados.peso_kg,
                        dados.altura_cm,
                        dados.condicoes_previas,
                        dados.historico_familiar,
                        estilo_vida,
                    ),
                )
            except Exception:
                cur.execute(
                    """
                    INSERT INTO perfis_saude (
                        usuario_id, idade, genero_biologico,
                        condicoes_previas, historico_familiar, estilo_vida
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING idade, genero_biologico, condicoes_previas,
                              historico_familiar, estilo_vida
                    """,
                    (
                        usuario_id,
                        dados.idade,
                        dados.genero_biologico,
                        dados.condicoes_previas or f"Peso {dados.peso_kg}kg",
                        dados.historico_familiar,
                        f"{estilo_vida}; altura {dados.altura_cm}cm",
                    ),
                )
            perfil = cur.fetchone()
    return dict(perfil)
