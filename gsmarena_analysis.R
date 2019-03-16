rm(list=ls())
setwd("/home/david/Documents/gsmarena-scraper")
Sys.setlocale("LC_TIME", "C")

library("viridis")
library("tidyverse")

# df <- read.delim("smartphones.csv", sep=';')
df_base <- read.delim("smartphones.csv", sep=';', stringsAsFactors = FALSE)

names(df_base)


df <- df_base %>%
  # Nouvelles variables, pas toutes utilisées
  mutate(           # Conversion en heure locale
                    datelist = str_split(as.character(year), c(', ', '. ')),
                    # Année = datelist <- datelist %>% pluck(1),
                    Année = unlist(lapply(datelist, `[`, c(1))),
                    Mois = unlist(lapply(datelist, `[`, c(2))),
                    Date = as.Date(str_c("01", Mois, Année, sep=' '), format="%d %B %Y"),
                    Marque = unlist(lapply(str_split(as.character(Nom), ' '), `[`, c(1))),
                    Poids = as.numeric(unlist(lapply(str_split(as.character(weight), ' '), `[`, c(1)))),
                    Taille_écran = as.numeric(gsub("\"", "",Taille_écran)),
                    # Diagonale = as.numeric(unlist(lapply(str_split(as.character(displaysize), ' '), `[`, c(1)))),
                    #Diagonale = as.numeric(gsub("\"", "", `Taille d'écran`)),
                    #Définition = gsub(" pixels", "", `Définition d'écran`),
                    Ratio = as.numeric(str_extract(str_extract(displaysize, regex("~(.*?) screen", dotall=TRUE)), regex("(?<=~)(.*?)(?=%)")))/100,
                    Hits = as.numeric(gsub(" hits", "", gsub(",", "", Hits))),
                    Batterie = as.numeric(unlist(lapply(str_split(batdescription1, " "), `[`, c(3)))),
                    # str_split(df$batdescription1[4], " ")[[1]][which(unlist(str_split(df$batdescription1[4], " ")) == "mAh") -1]
                    RAM = gsub(" RAM", "", unlist(lapply(str_split(internalmemory, ", "), `[`, c(2))))

                    ) %>%
  select(-c(datelist))

str(df)
names(df)

## Tableaux

df %>%
  arrange((Hits)) %>%
  head(50) %>%
  select(c(Marque, Nom, Année, Mois, Hits))

df %>%
  arrange(desc(Hits)) %>%
  head(50) %>%
  select(c(Marque, Nom, Année, Mois, Hits, Fans))

df %>%
  arrange(desc(Fans)) %>%
  head(50) %>%
  select(c(Marque, Nom, Année, Mois, Hits, Fans)) %>%
  View

df %>%
  arrange(desc(Taille_écran)) %>%
  head(50) %>%
  select(c(Marque, Nom, Année, Mois, Hits, Taille_écran)) %>%
  View

df %>%
  filter(gprstext == "No") %>%
  arrange(desc(Taille_écran)) %>%
  #head(50) %>%
  select(c(Marque, Nom, Année, Mois, Hits, Taille_écran)) %>%
  View

## Graphiques

df %>%
  filter(Année %in% 1990:2019) %>%
  ggplot(aes(Année, Ratio)) +
  geom_point(aes(size = Poids)) +
  geom_smooth(color = "gray20") +
  scale_color_viridis(discrete = TRUE) +
  labs(title = "", caption = "")

df %>%
  filter(Année %in% 1990:2019) %>%
  ggplot(aes(Année, Taille_écran)) +
  geom_point(aes(size = Poids)) +
  geom_smooth(color = "gray20") +
  scale_color_viridis(discrete = TRUE) +
  labs(title = "", caption = "")

df %>%
  filter(Année %in% 1990:2019) %>%
  ggplot(aes(Année, Poids)) +
  geom_point(aes(size = Ratio)) +
  geom_smooth(color = "gray20") +
  scale_color_viridis(discrete = TRUE) +
  labs(title = "", caption = "")

df %>%
  filter(Année %in% 1990:2019) %>%
  ggplot(aes(Année, Batterie)) +
  geom_point(aes(size = Poids)) +
  geom_smooth(color = "gray20") +
  scale_color_viridis(discrete = TRUE) +
  labs(title = "", caption = "")

df %>%
  filter(Année %in% 1990:2019) %>%
  filter(gprstext == "No") %>%
  ggplot(aes(Année)) +
  geom_bar(aes(fill=Marque)) +
  scale_color_viridis(discrete = TRUE) +
  labs(title = "", caption = "") +
  guides(fill=FALSE)

df %>%
  filter(Année %in% 1990:2019) %>%
  ggplot(aes(Année, Taille_écran)) +
  geom_boxplot() +
  geom_smooth(color = "gray20") +
  scale_color_viridis(discrete = TRUE) +
  labs(title = "", caption = "")

write_delim(df, "smartphones_cleaned.csv", delim=";")
