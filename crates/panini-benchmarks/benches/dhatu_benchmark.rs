use criterion::{black_box, criterion_group, criterion_main, Criterion};
use panini_core::dhatu::classifier::DhatuClassifier;
use panini_core::dhatu::emotion::EmotionalIntensity;
use panini_core::dhatu::profile::EmotionalProfile;

fn bench_text_classification(c: &mut Criterion) {
    let mut group = c.benchmark_group("Dhātu Classification");
    
    let classifier = DhatuClassifier::new();
    
    let texts = vec![
        ("short", "Hello world!"),
        ("medium", "This is a fascinating journey of exploration and discovery. \
                    We are seeking new knowledge and understanding."),
        ("long", "In the vast expanse of human consciousness, there exists a profound \
                  yearning for connection and understanding. This seeking drives us forward, \
                  pushing the boundaries of what we know and exploring the depths of what \
                  we feel. Through care and compassion, we forge bonds that transcend the \
                  individual, creating networks of meaning that span generations. Yet in \
                  this journey, we also encounter fear and uncertainty, the shadows that \
                  make our triumphs all the more meaningful."),
    ];
    
    for (name, text) in texts.iter() {
        group.bench_function(*name, |b| {
            b.iter(|| {
                classifier.classify_content(black_box(text))
            });
        });
    }
    
    group.finish();
}

fn bench_emotion_calculation(c: &mut Criterion) {
    let mut group = c.benchmark_group("Emotion Calculation");
    
    let mut intensity = EmotionalIntensity::new();
    intensity.set(panini_core::dhatu::emotion::PankseppEmotion::Seeking, 0.8);
    intensity.set(panini_core::dhatu::emotion::PankseppEmotion::Fear, 0.3);
    intensity.set(panini_core::dhatu::emotion::PankseppEmotion::Care, 0.6);
    
    group.bench_function("dominant_emotion", |b| {
        b.iter(|| {
            black_box(intensity.dominant())
        });
    });
    
    group.bench_function("arousal", |b| {
        b.iter(|| {
            black_box(intensity.arousal())
        });
    });
    
    group.finish();
}

fn bench_resonance_calculation(c: &mut Criterion) {
    use panini_core::dhatu::profile::EmotionalResonance;
    
    let mut intensity_a = EmotionalIntensity::new();
    intensity_a.set(panini_core::dhatu::emotion::PankseppEmotion::Seeking, 0.8);
    intensity_a.set(panini_core::dhatu::emotion::PankseppEmotion::Care, 0.5);
    let profile_a = EmotionalProfile::new("/test/a.txt".to_string(), intensity_a);
    
    let mut intensity_b = EmotionalIntensity::new();
    intensity_b.set(panini_core::dhatu::emotion::PankseppEmotion::Seeking, 0.7);
    intensity_b.set(panini_core::dhatu::emotion::PankseppEmotion::Play, 0.6);
    let profile_b = EmotionalProfile::new("/test/b.txt".to_string(), intensity_b);
    
    c.bench_function("resonance_calculation", |b| {
        b.iter(|| {
            EmotionalResonance::calculate(
                black_box(&profile_a),
                black_box(&profile_b)
            )
        });
    });
}

criterion_group!(
    benches,
    bench_text_classification,
    bench_emotion_calculation,
    bench_resonance_calculation
);
criterion_main!(benches);
