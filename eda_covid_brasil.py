import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

plt.rcParams["figure.dpi"] = 120
plt.rcParams["font.size"] = 10

dados_covid = pd.read_csv("owid-covid-data.csv", low_memory=False)  # low_memory evita que o pandas misture tipos de dados ao ler colunas muito grandes
dados_covid["date"] = pd.to_datetime(dados_covid["date"])

# aqui acontece a limpeza dos dados, separando os países das regiões/continentes, que estão todas juntas
areas_agregadas_para_remover = ["World", "Europe", "European Union", "Asia", "Africa",
         "North America", "South America", "Oceania",
         "High income", "Low income", "Upper middle income",
         "Lower middle income", "International"]
paises = dados_covid[~dados_covid["location"].isin(areas_agregadas_para_remover)].copy()
paises = paises[paises["continent"].notna()]

# ainda na parte de limpeza, filtrando o Brasil
dados_brasil = paises[paises["location"] == "Brazil"].copy()
dados_brasil = dados_brasil.sort_values("date")

colunas_series_temporais_brasil = ["new_cases_smoothed", "new_deaths_smoothed",
                                    "stringency_index", "people_fully_vaccinated_per_hundred"]
dados_brasil[colunas_series_temporais_brasil] = dados_brasil[colunas_series_temporais_brasil].interpolate(limit=14)
print("Período disponível para o Brasil:", dados_brasil["date"].min().date(),
      "a", dados_brasil["date"].max().date())
print("Linhas antes da limpeza:", len(dados_covid), "| Linhas de países válidos:", len(paises))
print("Valores nulos (Brasil) nas colunas-chave após interpolação:")
print(dados_brasil[colunas_series_temporais_brasil].isna().sum())

# fazendo o cruzamento de indicadores socioeconômicos com as mortes, comparando países para ver se existe relação entre pobreza e mortes pela pandemia
ultimo_registro_por_pais = (
    paises.sort_values("date")
    .groupby("location")
    .last()
    .reset_index()
)
colunas_comparativo_social = ["location", "continent", "gdp_per_capita", "human_development_index",
                               "extreme_poverty", "total_deaths_per_million",
                               "excess_mortality_cumulative_per_million", "population"]
comparativo_social = ultimo_registro_por_pais[colunas_comparativo_social].dropna(
    subset=["gdp_per_capita", "human_development_index", "total_deaths_per_million"]
)
print("\nPaíses com dados socioeconômicos completos para comparação:", len(comparativo_social))

# primeiro insight: houveram políticas preventiva/reativa tanto global quanto no Brasil? fazendo uma comparação entre a média global e o Brasil, para ver se o Brasil foi mais ou menos rigido que a media global 
correlacoes_casos_rigidez_por_pais = []
for local, dados_do_pais in paises.groupby("location"):
    corr_pais = dados_do_pais[["new_cases_smoothed", "stringency_index"]].corr().iloc[0, 1]
    if pd.notna(corr_pais):
        correlacoes_casos_rigidez_por_pais.append(corr_pais)
correlacao_media_global_casos_rigidez = np.mean(correlacoes_casos_rigidez_por_pais)
# recorte do Brasil
correlacao_casos_rigidez = dados_brasil[["new_cases_smoothed", "stringency_index"]].corr().iloc[0, 1]
print(f"\nCorrelação média global casos x rigidez ({len(correlacoes_casos_rigidez_por_pais)} países): {correlacao_media_global_casos_rigidez:.2f}")
print(f"Correlação (defasagem 0) casos x rigidez no Brasil: {correlacao_casos_rigidez:.2f}")
print(f"Brasil x média global: {correlacao_casos_rigidez:.2f} vs {correlacao_media_global_casos_rigidez:.2f}")

fig1, eixo1 = plt.subplots(figsize=(10, 5))
eixo1.plot(dados_brasil["date"], dados_brasil["new_cases_smoothed"], color="#c0392b", lw=2, label="Novos Casos")
eixo1.set_ylabel("Novos Casos (Média Móvel)", color="#c0392b")
eixo1.tick_params(axis="y", labelcolor="#c0392b")
eixo1.set_xlabel("Data")

eixo1_sub = eixo1.twinx()
eixo1_sub.fill_between(dados_brasil["date"], dados_brasil["stringency_index"], color="#2980b9", alpha=0.25, label="Índice de Rigidez")
eixo1_sub.set_ylabel("Índice de Rigidez (%)", color="#2980b9")
eixo1_sub.tick_params(axis="y", labelcolor="#2980b9")
eixo1_sub.set_ylim(0, 100)

eixo1.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
eixo1.xaxis.set_major_formatter(mdates.DateFormatter("%b/%y"))
plt.title("Brasil: Novos Casos x Rigidez das Restrições")
fig1.autofmt_xdate()
fig1.tight_layout()
fig1.savefig("grafico1_rigidez_vs_casos.png")
plt.close(fig1)

# segundo insight: a vacinação coincidir com a queda de mortes? aqui também faço a comparação do brasil com a media global para ver como o Brasil se saiu
fig2, eixo2 = plt.subplots(figsize=(10, 5))
eixo2.bar(dados_brasil["date"], dados_brasil["new_deaths_smoothed"], color="#8e44ad", alpha=0.5, width=2, label="Novos Óbitos")
eixo2.set_ylabel("Novos óbitos (média móvel 7d)", color="#8e44ad")
eixo2.tick_params(axis="y", labelcolor="#8e44ad")
eixo2.set_xlabel("Data")

eixo2_sub = eixo2.twinx()
eixo2_sub.plot(dados_brasil["date"], dados_brasil["people_fully_vaccinated_per_hundred"], color="#27ae60", lw=2.5, label="% População Vacinada")
eixo2_sub.set_ylabel("% população totalmente vacinada", color="#27ae60")
eixo2_sub.tick_params(axis="y", labelcolor="#27ae60")
eixo2_sub.set_ylim(0, 100)

eixo2.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
eixo2.xaxis.set_major_formatter(mdates.DateFormatter("%b/%y"))
plt.title("Brasil: Avanço da vacinação x Óbitos diários (2020-2024)")
fig2.autofmt_xdate()
fig2.tight_layout()
fig2.savefig("grafico2_vacinacao_vs_obitos.png")
plt.close(fig2)

correlacoes_vacinacao_obitos_por_pais = []
for local, dados_do_pais in paises.groupby("location"):
    corr_pais = dados_do_pais[["new_deaths_smoothed", "people_fully_vaccinated_per_hundred"]].corr().iloc[0, 1]
    if pd.notna(corr_pais):
        correlacoes_vacinacao_obitos_por_pais.append(corr_pais)
correlacao_media_global_vacinacao_obitos = np.mean(correlacoes_vacinacao_obitos_por_pais)
# recorte do Brasil
correlacao_vacinacao_obitos_brasil = dados_brasil[["new_deaths_smoothed", "people_fully_vaccinated_per_hundred"]].corr().iloc[0, 1]
print(f"\nCorrelação média global vacinação x óbitos ({len(correlacoes_vacinacao_obitos_por_pais)} países): {correlacao_media_global_vacinacao_obitos:.2f}")
print(f"Correlação vacinação x óbitos no Brasil: {correlacao_vacinacao_obitos_brasil:.2f}")
print(f"Brasil x média global: {correlacao_vacinacao_obitos_brasil:.2f} vs {correlacao_media_global_vacinacao_obitos:.2f}")

# terceiro insight: paises mais pobres tiveram mortalidade em excesso maior?
figura, eixo_dispersao = plt.subplots(figsize=(8, 6))
dados_mortalidade_excesso = comparativo_social.dropna(subset=["excess_mortality_cumulative_per_million"])
cores_continente = {"South America": "#e74c3c", "Africa": "#f39c12", "Asia": "#3498db",
         "Europe": "#2ecc71", "North America": "#9b59b6", "Oceania": "#1abc9c"}
for continente, dados_continente in dados_mortalidade_excesso.groupby("continent"):
    eixo_dispersao.scatter(dados_continente["gdp_per_capita"], dados_continente["excess_mortality_cumulative_per_million"],
                            label=continente, color=cores_continente.get(continente, "gray"), alpha=0.75, s=40)
brasil_destaque = dados_mortalidade_excesso[dados_mortalidade_excesso["location"] == "Brazil"]
if not brasil_destaque.empty:
    eixo_dispersao.scatter(brasil_destaque["gdp_per_capita"], brasil_destaque["excess_mortality_cumulative_per_million"],
                            color="black", s=140, marker="*", label="Brasil", zorder=5)
eixo_dispersao.set_xscale("log")
eixo_dispersao.set_xlabel("PIB per capita (US$, escala log)")
eixo_dispersao.set_ylabel("Mortalidade em excesso acumulada (por milhão)")
eixo_dispersao.set_title("PIB per capita x Mortalidade em excesso por país")
eixo_dispersao.legend(fontsize=8, loc="upper right")
figura.tight_layout()
figura.savefig("grafico3_pib_vs_mortalidade.png")
plt.close(figura)

correlacao_pib_mortalidade = dados_mortalidade_excesso[["gdp_per_capita", "excess_mortality_cumulative_per_million"]].corr().iloc[0, 1]
print(f"\nCorrelação PIB per capita x mortalidade em excesso (global): {correlacao_pib_mortalidade:.2f}")