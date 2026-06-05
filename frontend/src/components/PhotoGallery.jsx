import { useState } from 'react';
import Lightbox from "yet-another-react-lightbox";
import "yet-another-react-lightbox/styles.css";
import './PhotoGallery.css';

// --- AQUÍ DEBES AÑADIR TUS FOTOS ---
// Agrega los objetos de imagen que quieras mostrar.
// Asegúrate de que las imágenes estén en la carpeta `frontend/public/gallery/`
const images = [
  { src: "/foto_salon.jpeg" },
  { src: "/foto_salon_1.jpeg" },
  { src: "/foto_salon_2.jpeg" },
  { src: "/foto_salon_3.jpeg" },
  { src: "/foto_salon_4.jpeg" },
  { src: "/foto_salon_5.jpeg" },
  { src: "/foto_salon_6.jpeg" },
  { src: "/foto_salon_7.jpeg" },
  { src: "/foto_salon_8.jpeg" },
  { src: "/foto_salon_9.jpg" },
  { src: "/foto_salon_10.jpg" },
  { src: "/foto_salon_11.jpg" },
];

function PhotoGallery() {
    const [index, setIndex] = useState(-1);

    return (
        <>
            <div className="photo-gallery-grid">
                {images.map((image, idx) => (
                    <div
                        key={idx}
                        className="gallery-image-container"
                        onClick={() => setIndex(idx)}
                    >
                        <img
                            src={image.src}
                            alt={`Foto del salón ${idx + 1}`}
                            className="gallery-image"
                        />
                         <div className="gallery-image-overlay"></div>
                    </div>
                ))}
            </div>

            <Lightbox
                open={index >= 0}
                index={index}
                close={() => setIndex(-1)}
                slides={images}
            />
        </>
    );
}

export default PhotoGallery;