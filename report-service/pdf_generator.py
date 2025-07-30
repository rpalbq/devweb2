from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime, timedelta
import models

def get_mood_name(emoji):
    """Mapear emojis para nomes"""
    mood_names = {
        '😊': 'Feliz',
        '😢': 'Triste', 
        '😡': 'Bravo',
        '😰': 'Ansioso',
        '😴': 'Cansado',
        '🥳': 'Animado',
        '😍': 'Apaixonado',
        '🤔': 'Pensativo'
    }
    return mood_names.get(emoji, 'Desconhecido')

def generate_mood_report_pdf(user_id, days=30, is_professional=False):
    """
    Gerar PDF do relatório de humor
    
    Args:
        user_id: ID do usuário
        days: Período em dias (padrão 30)
        is_professional: Se True, inclui informações adicionais para profissionais
    
    Returns:
        BytesIO: Buffer com o PDF gerado
    """
    
    # Buscar dados
    stats = models.get_user_mood_stats(user_id, days=days)
    
    if 'error' in stats:
        raise Exception(f"Erro ao gerar dados: {stats['error']}")
    
    # Criar buffer para o PDF
    buffer = BytesIO()
    
    # Configurar documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo customizado para título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#4f46e5')
    )
    
    # Estilo para subtítulos
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#6366f1')
    )
    
    # Estilo para texto normal
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12
    )
    
    # Lista para elementos do PDF
    elements = []
    
    #  CABEÇALHO
    elements.append(Paragraph("🎭 Relatório de Humor", title_style))
    elements.append(Spacer(1, 12))
    
    # Informações básicas
    user_info = stats.get('user_info', {})
    username = user_info.get('username', 'Usuário')
    
    if is_professional:
        elements.append(Paragraph(f"<b>Paciente:</b> {username}", normal_style))
    else:
        elements.append(Paragraph(f"<b>Usuário:</b> {username}", normal_style))
    
    elements.append(Paragraph(f"<b>Período:</b> Últimos {days} dias", normal_style))
    now_local = datetime.now()
    now_brazil = datetime.utcnow() - timedelta(hours=3)
    elements.append(Paragraph(f"<b>Gerado em:</b> {now_brazil.strftime('%d/%m/%Y às %H:%M')}", normal_style))
    elements.append(Spacer(1, 20))
    
    # 📊 RESUMO GERAL
    elements.append(Paragraph("📊 Resumo Geral", subtitle_style))
    
    summary_data = [
        ['Métrica', 'Valor'],
        ['Total de registros (período)', str(stats.get('total_entries_period', 0))],
        ['Total de registros (geral)', str(stats.get('total_entries_all_time', 0))],
        ['Dias com registros', f"{stats.get('unique_days_with_entries', 0)}/{days}"],
        ['Humor mais comum', f"{stats.get('most_common_mood', 'N/A')} ({get_mood_name(stats.get('most_common_mood', ''))})"],
        ['Variedade de humores', str(len(stats.get('mood_distribution', [])))]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0'))
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    #  DISTRIBUIÇÃO DE HUMOR
    if stats.get('mood_distribution'):
        elements.append(Paragraph("🎭 Distribuição de Humor", subtitle_style))
        
        mood_data = [['Emoji', 'Humor', 'Quantidade', 'Porcentagem']]
        total_entries = stats['total_entries_period']
        
        for mood in stats['mood_distribution']:
            emoji = mood['_id']
            name = get_mood_name(emoji)
            count = mood['count']
            percentage = round((count / total_entries) * 100, 1) if total_entries > 0 else 0
            
            mood_data.append([emoji, name, str(count), f"{percentage}%"])
        
        mood_table = Table(mood_data, colWidths=[0.8*inch, 1.5*inch, 1*inch, 1*inch])
        mood_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0'))
        ]))
        
        elements.append(mood_table)
        elements.append(Spacer(1, 20))
    
    # 🎵 TOP MÚSICAS (se houver)
    if stats.get('top_songs') and len(stats['top_songs']) > 0:
        elements.append(Paragraph("🎵 Músicas Mais Associadas", subtitle_style))
        
        songs_data = [['#', 'Música', 'Artista', 'Vezes']]
        
        for i, song in enumerate(stats['top_songs'][:5], 1):
            songs_data.append([
                str(i),
                song.get('song_title', 'N/A'),
                song.get('song_artist', 'N/A'),
                str(song.get('count', 0))
            ])
        
        songs_table = Table(songs_data, colWidths=[0.5*inch, 2*inch, 1.5*inch, 0.8*inch])
        songs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Centralizar coluna #
            ('ALIGN', (-1, 0), (-1, -1), 'CENTER'),  # Centralizar coluna Vezes
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0'))
        ]))
        
        elements.append(songs_table)
        elements.append(Spacer(1, 20))
    
    # 💡 INSIGHTS SIMPLES
    elements.append(Paragraph("💡 Observações", subtitle_style))
    
    insights = []
    
    if stats['total_entries_period'] == 0:
        insights.append("• Nenhum registro encontrado neste período.")
    else:
        activity_level = stats.get('report_summary', {}).get('activity_level', 'Baixo')
        insights.append(f"• Nível de atividade: {activity_level}")
        
        if stats.get('most_common_mood'):
            mood_name = get_mood_name(stats['most_common_mood'])
            insights.append(f"• Humor predominante: {mood_name}")
        
        consistency = stats.get('unique_days_with_entries', 0)
        insights.append(f"• Registrou humor em {consistency} de {days} dias")
        
        if stats.get('top_songs'):
            top_song = stats['top_songs'][0]
            insights.append(f"• Música mais registrada: \"{top_song.get('song_title', 'N/A')}\"")
    
    for insight in insights:
        elements.append(Paragraph(insight, normal_style))
    
    elements.append(Spacer(1, 30))
    
    #  RODAPÉ
    if is_professional:
        footer_text = "Este relatório foi gerado para fins profissionais de acompanhamento psicológico."
    else:
        footer_text = "Este é seu relatório pessoal de humor. Utilize-o para acompanhar seu bem-estar."
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph(footer_text, footer_style))
    elements.append(Paragraph(f"Gerado por Registra.Mood em {now_brazil.strftime('%d/%m/%Y')}", footer_style))
    
    # Construir PDF
    doc.build(elements)
    
    # Retornar buffer
    buffer.seek(0)
    return buffer

def create_simple_pdf_test():
    """Função simples para testar se o PDF está funcionando"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    elements = [
        Paragraph("🎭 Teste PDF - Registra.Mood", styles['Title']),
        Spacer(1, 12),
        Paragraph("Se você está vendo isto, o PDF está funcionando! 🎉", styles['Normal'])
    ]
    
    doc.build(elements)
    buffer.seek(0)
    return buffer