import scrapy
import re

class NewsSpider(scrapy.Spider):
    name = "news"

    start_urls = [
        'https://selesnafes.com/2025/01/batismo-de-mangueira-marca-acolhimento-de-novos-alunos-em-escola-militar/',
        'https://g1.globo.com/economia/noticia/2025/01/31/petrobras-anuncia-aumento-do-preco-do-diesel-para-as-distribuidoras.ghtml',
        'https://esportes.r7.com/lance/o-principe-esta-de-volta-santos-anuncia-oficialmente-retorno-de-neymar-apos-12-anos-31012025/',
        'https://www.band.uol.com.br/esportes/futebol/campeonato-saudita/noticias/al-hilal-apresenta-super-proposta-ao-real-madrid-por-rodrygo-diz-jornal-202501311403',
        'https://g1.globo.com/rr/roraima/noticia/2025/02/03/agencia-da-onu-volta-a-atender-migrantes-venezuelanos-em-roraima.ghtml',
        'https://selesnafes.com/2025/02/licenca-para-petrobras-na-foz-do-amazonas-pode-sair-apos-marco-diz-ibama/',
        'https://www.band.uol.com.br/noticias/celulares-proibidos-nas-escolas-lei-202502031330',
        'https://esportes.r7.com/lance/cedric-explica-motivo-de-ter-escolhido-o-sao-paulo-e-avalia-calendario-brasileiro-vou-me-adaptar-03022025/',
        'https://www.cleidefreires.com.br/policia-civil-do-ap-pede-colaboracao-da-populacao-para-localizar-dois-acusados-de-ordenar-morte-de-missionario/',
        'https://www.luizmelo.blog.br/2025/02/sentimento-23/',
        'https://www1.folha.uol.com.br/cotidiano/2022/06/desigualdade-emperra-avanco-da-mobilidade-em-sao-paulo.shtml'
        # 'https://noticias.uol.com.br/colunas/jamil-chade/2025/02/05/onu-diz-que-plano-de-trump-e-ilegal-e-fara-cupula-para-reconhecer-palestina.htm'
        # 'https://www.folhape.com.br/noticias/cia-oferece-incentivos-para-demissao-voluntaria-para-funcionarios/389503/'
    ]

    def start_requests(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        for url in self.start_urls:
            yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):
        news_title = response.xpath("translate(//h1[contains(@class, 'base') or contains(@class, 'title')]/text(), '“”', '')").get()

        if not news_title:
            news_title = response.xpath("(//h1/text())[1]").get()

        # tratando os parágrafos com conteúdo das notícias.
        paragraphs = response.xpath("//div[contains(@class, 'article__content')]//p//text()").getall()

        if not paragraphs:
            # paragraphs = response.xpath("//article[contains(@itemprop,'articleBody')]//p//text()").getall()
            paragraphs = response.xpath("(//p[contains(@class,'content-text__container')])//text()").getall()

        if not paragraphs:
            # paragraphs = response.xpath("//div[contains(@class,'content')]/following-sibling::p//text()").getall()
            paragraphs = response.xpath("//div[contains(@class,'entry-content read-details')]/p/text()").getall()

        if not paragraphs:
            paragraphs = response.xpath("//span[contains(@class,'b-article-body__text')]//text()").getall()

        # if not paragraphs:
        #     paragraphs = response.xpath("//span/text()").getall()

        if not paragraphs:
            paragraphs = response.xpath("//p//text()").getall()


        # tratando os parágrafos
        clean_paragraphs = [p.replace('\u00a0', ' ')
                            .strip() for p in paragraphs]

        # Removendo os textos indesejados
        unwanted_texts = [
            "(adsbygoogle = window.adsbygoogle || []).push({});",
            "[email protected]",
            "Todos os direitos reservados. Desenvolvido por",
            "André Melo"
        ]

        for i in range(len(clean_paragraphs)):
            print(clean_paragraphs[i])
            for unwanted in unwanted_texts:
                clean_paragraphs[i] = clean_paragraphs[i].replace(unwanted, "")

        clean_paragraphs = [
            re.sub(r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})\b', '', p) for p in clean_paragraphs
        ]

        clean_paragraphs = [
            re.sub(r'[\r\n]+', ' ', p) for p in clean_paragraphs
        ]

        # Junta todos os parágrafos para formar o conteúdo completo
        news_content = ' '.join(clean_paragraphs).strip()

        # capturando autores
        autor = response.xpath("//p[contains(@class,'content-publication-data__from')]//text()").getall()

        if not autor:
            autor = response.xpath("//i[contains(@class,'far fa-user-circle')]/parent::span/a/text()").getall()

        if not autor:
            autor = response.xpath("//div//p[contains(@class,'article-text')]//text()[not(ancestor::time)]").getall()

        if not autor:
            autor = response.xpath("//app-author//text()[not(ancestor::span)]").getall()

        if not autor:
            autor = response.xpath("(//span[contains(@class, 'author')]/a/text())[1]").getall()

        if not autor:
            autor = response.xpath("//span[contains(@class, 'author')]//text()").getall()

        if not autor:
            autor = response.xpath("(//*[contains(@class,'author')])[1]//text()").getall()

        if not autor:
            autor = response.xpath("//*[contains(@class,'Autor')]//text()").getall()

        autor = ' '.join(autor).strip()

        # capturando datas
        date = response.xpath("(//time)[1]/text()").getall()

        if not date:
            date = response.xpath("(//span[contains(@class, 'posts-date')])[1]/a/text()").getall()

        if not date:
            date = response.xpath("//div[contains(@class, 'evo-post-date')]//a/text()").getall()

        date = ' '.join(date).strip()

        # montando o json
        yield {
            'url': response.url,
            'title': news_title,
            'contents': news_content,
            'author': autor,
            'date': date
        }