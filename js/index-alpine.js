/**
 * Home page view model for Alpine.js.
 * Keeps repetitive content in one place and preserves i18n keys in the template.
 */
function homePageData() {
    return {
        aboutCards: [
            {
                featured: true,
                icon: 'bar-chart-2',
                titleKey: 'about.card1.title',
                title: 'Langzeitstudie',
                subtitleKey: 'about.card1.subtitle',
                subtitle: 'Jaehrliche Erhebungen ermoeglichen die Analyse von Trends und Entwicklungen'
            },
            {
                featured: false,
                icon: 'building-2',
                titleKey: 'about.card2.title',
                title: 'Branchenuebergreifend',
                subtitleKey: 'about.card2.subtitle',
                subtitle: 'Teilnehmer aus Konzernen, Mittelstand und Startups verschiedener Branchen'
            },
            {
                featured: false,
                icon: 'flask-conical',
                titleKey: 'about.card3.title',
                title: 'Wissenschaftlich fundiert',
                subtitleKey: 'about.card3.subtitle',
                subtitle: 'Peer-reviewed Publikationen und offene Methodik'
            }
        ],

        surveys: [
            {
                featured: true,
                statusKey: 'surveys.card1.status',
                status: 'AKTIV',
                statusStyle: '',
                titleKey: 'surveys.card1.title',
                title: 'KI im IT-Arbeitsalltag 2026',
                descriptionKey: 'surveys.card1.description',
                description: 'Die aktuelle Erhebung untersucht die fortschreitende Integration von GenAI in der deutschen IT-Branche.',
                matrixItems: [
                    {
                        labelKey: 'surveys.card1.period',
                        label: 'Zeitraum',
                        valueKey: 'surveys.card1.periodValue',
                        value: 'Q1 2026',
                        valueStyle: 'font-size:0.875rem;'
                    },
                    {
                        labelKey: 'surveys.card1.duration',
                        label: 'Dauer',
                        valueKey: 'surveys.card1.durationValue',
                        value: '3-5 Minuten',
                        valueStyle: 'font-size:0.875rem;'
                    },
                    {
                        labelKey: 'surveys.card1.goal',
                        label: 'Ziel',
                        valueKey: 'surveys.card1.goalValue',
                        value: '500+',
                        valueStyle: ''
                    }
                ],
                
                note: null,
                footerStyle: 'justify-content:center;'
            },
            {
                featured: false,
                statusKey: 'surveys.card2.status',
                status: 'ABGESCHLOSSEN',
                statusStyle: 'color:#2E7D32;',
                titleKey: 'surveys.card2.title',
                title: 'KI im IT-Arbeitsalltag 2024/25',
                descriptionKey: 'surveys.card2.description',
                description: 'Erste umfassende Erhebung zur GenAI-Adoption in der deutschen IT-Branche mit 174 Teilnehmern.',
                matrixItems: [
                    {
                        labelKey: 'surveys.card2.participants',
                        label: 'Teilnehmer',
                        valueKey: 'surveys.card2.participantsValue',
                        value: '174',
                        valueStyle: ''
                    },
                    {
                        labelKey: 'surveys.card2.status2',
                        label: 'Status',
                        valueKey: 'surveys.card2.statusValue',
                        value: 'Veroeffentlicht',
                        valueStyle: 'font-size:0.875rem;'
                    }
                ],
                actions: [
                    {
                        href: 'ergebnisse-2024.html',
                        className: 'btn',
                        style: 'background:var(--th-blue);color:white;margin:0;',
                        i18nKey: 'surveys.card2.cta1',
                        label: 'Ergebnisse ansehen',
                        download: false
                    },
                    {
                        href: 'AI_Survey_Paper2024.pdf',
                        className: 'btn',
                        style: 'background:white;color:var(--th-blue);border:2px solid var(--th-blue);margin:0;',
                        i18nKey: 'surveys.card2.cta2',
                        label: 'Paper (PDF)',
                        download: true
                    }
                ],
                note: null,
                footerStyle: 'justify-content:center;gap:1rem;'
            },
            {
                featured: false,
                statusKey: 'surveys.card3.status',
                status: 'GEPLANT',
                statusStyle: 'color:#9E9E9E;',
                titleKey: 'surveys.card3.title',
                title: 'KI im IT-Arbeitsalltag 2027',
                descriptionKey: 'surveys.card3.description',
                description: 'Die Fortsetzung unserer Langzeitstudie mit erweiterten Fragestellungen.',
                matrixItems: [
                    {
                        labelKey: 'surveys.card3.period',
                        label: 'Zeitraum',
                        valueKey: 'surveys.card3.periodValue',
                        value: 'Q1 2027',
                        valueStyle: 'font-size:0.875rem;'
                    }
                ],
                actions: [],
                note: {
                    key: 'surveys.card3.planning',
                    text: 'Planung startet im Q3 2026'
                },
                footerStyle: 'justify-content:center;'
            }
        ],

        highlights: [
            {
                valueHtml: '76.5<span>%</span>',
                labelKey: 'surveys.highlights.stat1',
                label: 'nutzen GenAI beruflich'
            },
            {
                valueHtml: '84.8<span>%</span>',
                labelKey: 'surveys.highlights.stat2',
                label: 'sehen Produktivitaetsgewinn'
            },
            {
                valueHtml: '50<span>%</span>',
                labelKey: 'surveys.highlights.stat3',
                label: 'betrachten Datensicherheit als Huerde'
            },
            {
                valueHtml: '100<span>%</span>',
                labelKey: 'surveys.highlights.stat4',
                label: 'Adoption bei Beratungen'
            }
        ]
    };
}
