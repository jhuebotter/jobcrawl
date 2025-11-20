import React, { useEffect } from 'react';
import {
  MapContainer,
  TileLayer,
  Marker,
  useMap,
  useMapEvents,
} from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Guard against undefined prototype in some bundler/env combos
try {
  if (L.Icon?.Default?.prototype?._getIconUrl) {
    // Fix for default marker icon issue with webpack/Vite
    delete L.Icon.Default.prototype._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl:
        'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
      iconUrl:
        'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
      shadowUrl:
        'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
    });
  }
} catch (e) {
  console.warn('Leaflet icon patch failed (non-fatal):', e);
}

function ChangeView({ center, zoom }) {
  const map = useMap();

  useEffect(() => {
    if (center) {
      map.flyTo(center, zoom);
    }
  }, [center, zoom, map]);

  return null;
}

function LocationMarker({ setLocation, setPosition, position }) {
  useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng;
      setPosition(e.latlng);

      // Reverse geocoding using Nominatim API
      fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`
      )
        .then((res) => res.json())
        .then((data) => {
          const address = data.address || {};
          setLocation({
            city:
              address.city ||
              address.town ||
              address.village ||
              'N/A',
            country: address.country || 'N/A',
          });
        })
        .catch((err) => {
          console.error('Error fetching location data:', err);
          setLocation({
            city: 'Error',
            country: 'Could not fetch data',
          });
        });
    },
  });

  if (!position) return null;
  return <Marker position={position} />;
}

export default function MapComponent({ setLocation, setPosition, position }) {
  // Fallback center if no position yet
  const center = position || { lat: 20, lng: 0 };
  const zoom = position ? 10 : 2;

  return (
    <MapContainer
      center={[center.lat, center.lng]}
      zoom={zoom}
      scrollWheelZoom={true}
      style={{ height: '400px', width: '100%' }}
    >
      <ChangeView center={position && [position.lat, position.lng]} zoom={zoom} />
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <LocationMarker
        setLocation={setLocation}
        setPosition={setPosition}
        position={position}
      />
    </MapContainer>
  );
}
