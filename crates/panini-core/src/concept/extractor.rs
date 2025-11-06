//! Concept Extractors - Extract semantic concepts from text

use super::{Concept, ConceptType, ConceptVersion, EntitySubtype};
use std::collections::HashMap;

pub trait ConceptExtractor: Send + Sync {
    fn extract(&self, text: &str, source_chunk: &str) -> Vec<Concept>;
    fn name(&self) -> &str;
}

pub struct NERExtractor {
    patterns: HashMap<String, EntitySubtype>,
}

impl NERExtractor {
    pub fn new() -> Self {
        let mut patterns = HashMap::new();
        patterns.insert("inc.".to_lowercase(), EntitySubtype::Organization);
        patterns.insert("corp.".to_lowercase(), EntitySubtype::Organization);
        patterns.insert("university".to_lowercase(), EntitySubtype::Organization);
        Self { patterns }
    }

    fn is_proper_noun(word: &str) -> bool {
        !word.is_empty() && word.chars().next().unwrap().is_uppercase() && word.len() > 2
    }

    fn extract_entities(&self, text: &str) -> Vec<(String, EntitySubtype)> {
        let mut entities = Vec::new();
        let words: Vec<&str> = text.split_whitespace().collect();
        
        let mut i = 0;
        while i < words.len() {
            let word = words[i].trim_matches(|c: char| !c.is_alphanumeric());
            
            if i + 1 < words.len() && Self::is_proper_noun(word) {
                let next_word = words[i + 1].trim_matches(|c: char| !c.is_alphanumeric());
                if Self::is_proper_noun(next_word) {
                    let entity = format!("{} {}", word, next_word);
                    let subtype = if self.is_organization(&entity) {
                        EntitySubtype::Organization
                    } else {
                        EntitySubtype::Person
                    };
                    entities.push((entity, subtype));
                    i += 2;
                    continue;
                }
            }
            
            if Self::is_proper_noun(word) {
                entities.push((word.to_string(), EntitySubtype::Other));
            }
            i += 1;
        }
        entities
    }

    fn is_organization(&self, text: &str) -> bool {
        let lower = text.to_lowercase();
        self.patterns.iter().any(|(pattern, subtype)| {
            matches!(subtype, EntitySubtype::Organization) && lower.contains(pattern)
        })
    }
}

impl ConceptExtractor for NERExtractor {
    fn extract(&self, text: &str, source_chunk: &str) -> Vec<Concept> {
        let entities = self.extract_entities(text);
        let timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();

        entities.into_iter().map(|(entity, subtype)| {
            let mut concept = Concept::new(entity.clone(), ConceptType::NamedEntity);
            concept.entity_subtype = Some(subtype);
            let version = ConceptVersion {
                version_id: uuid::Uuid::new_v4().to_string(),
                text: entity,
                language: "en".to_string(),
                source_chunk: source_chunk.to_string(),
                timestamp,
                confidence: 0.7,
                context: None,
            };
            concept.add_version(version);
            concept
        }).collect()
    }

    fn name(&self) -> &str {
        "NER-Basic"
    }
}

pub struct WikipediaExtractor;

impl WikipediaExtractor {
    pub fn new() -> Self {
        Self
    }

    fn extract_wiki_links(&self, text: &str) -> Vec<String> {
        let mut links = Vec::new();
        let mut chars = text.chars().peekable();
        
        while let Some(c) = chars.next() {
            if c == '[' && chars.peek() == Some(&'[') {
                chars.next();
                let mut link = String::new();
                
                while let Some(c) = chars.next() {
                    if c == ']' && chars.peek() == Some(&']') {
                        chars.next();
                        break;
                    }
                    if c == '|' {
                        while let Some(c) = chars.next() {
                            if c == ']' && chars.peek() == Some(&']') {
                                chars.next();
                                break;
                            }
                        }
                        break;
                    }
                    link.push(c);
                }
                
                if !link.is_empty() {
                    links.push(link.trim().to_string());
                }
            }
        }
        links
    }

    fn extract_categories(&self, text: &str) -> Vec<String> {
        text.lines()
            .filter_map(|line| {
                let trimmed = line.trim();
                if trimmed.starts_with("[[Category:") || trimmed.starts_with("[[category:") {
                    trimmed.find("]]").map(|end| trimmed[11..end].to_string())
                } else {
                    None
                }
            })
            .collect()
    }
}

impl ConceptExtractor for WikipediaExtractor {
    fn extract(&self, text: &str, source_chunk: &str) -> Vec<Concept> {
        let mut concepts = Vec::new();
        let timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();

        for link in self.extract_wiki_links(text) {
            let mut concept = Concept::new(link.clone(), ConceptType::TechnicalTerm);
            let version = ConceptVersion {
                version_id: uuid::Uuid::new_v4().to_string(),
                text: link,
                language: "en".to_string(),
                source_chunk: source_chunk.to_string(),
                timestamp,
                confidence: 0.9,
                context: None,
            };
            concept.add_version(version);
            concepts.push(concept);
        }

        for category in self.extract_categories(text) {
            let mut concept = Concept::new(category.clone(), ConceptType::Category);
            let version = ConceptVersion {
                version_id: uuid::Uuid::new_v4().to_string(),
                text: category,
                language: "en".to_string(),
                source_chunk: source_chunk.to_string(),
                timestamp,
                confidence: 1.0,
                context: None,
            };
            concept.add_version(version);
            concept.metadata.insert("source".to_string(), "wikipedia_category".to_string());
            concepts.push(concept);
        }

        concepts
    }

    fn name(&self) -> &str {
        "Wikipedia"
    }
}
