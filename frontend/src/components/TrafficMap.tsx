import React from 'react';
import { MapContainer, TileLayer, Polyline, CircleMarker, Popup } from 'react-leaflet';
import { LatLngExpression } from 'leaflet';
import { TrafficNetwork, NetworkStatus, CongestionLevel } from '../types';

interface TrafficMapProps {
  network: TrafficNetwork | null;
  networkStatus: NetworkStatus | null;
  selectedSegmentId: string | null;
  onSegmentSelect: (segmentId: string | null) => void;
}

const getCongestionColor = (level: CongestionLevel): string => {
  switch (level) {
    case 'low': return '#4caf50';
    case 'medium': return '#ff9800';
    case 'high': return '#f44336';
    case 'gridlock': return '#000000';
    default: return '#666666';
  }
};

const getSegmentOpacity = (segmentId: string, selectedSegmentId: string | null): number => {
  if (!selectedSegmentId) return 1.0;
  return segmentId === selectedSegmentId ? 1.0 : 0.6;
};

const TrafficMap: React.FC<TrafficMapProps> = ({
  network,
  networkStatus,
  selectedSegmentId,
  onSegmentSelect
}) => {
  if (!network) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#fff' }}>
        <p>Loading map...</p>
      </div>
    );
  }

  // Calculate map center based on network coordinates
  const allCoordinates = Object.values(network.segments).flatMap(segment => segment.coordinates);
  const centerLat = allCoordinates.reduce((sum, coord) => sum + coord[0], 0) / allCoordinates.length;
  const centerLng = allCoordinates.reduce((sum, coord) => sum + coord[1], 0) / allCoordinates.length;
  const center: LatLngExpression = [centerLat, centerLng];

  return (
    <MapContainer
      center={center}
      zoom={15}
      style={{ height: '100%', width: '100%' }}
      onClick={() => onSegmentSelect(null)}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Render road segments */}
      {Object.values(network.segments).map(segment => {
        const status = networkStatus?.[segment.id];
        const congestionLevel = status?.congestion_level || 'low';
        const color = getCongestionColor(congestionLevel);
        const opacity = getSegmentOpacity(segment.id, selectedSegmentId);

        if (segment.segment_type === 'road') {
          return (
            <Polyline
              key={segment.id}
              positions={segment.coordinates as LatLngExpression[]}
              color={color}
              weight={6}
              opacity={opacity}
              eventHandlers={{
                click: (e) => {
                  e.originalEvent.stopPropagation();
                  onSegmentSelect(segment.id);
                }
              }}
            >
              <Popup>
                <div>
                  <h4>{segment.name}</h4>
                  <p><strong>Type:</strong> Road Segment</p>
                  <p><strong>Capacity:</strong> {segment.capacity} veh/hr</p>
                  <p><strong>Current Queue:</strong> {status?.current_queue?.toFixed(1) || 'N/A'} vehicles</p>
                  <p><strong>Current Flow:</strong> {status?.current_flow?.toFixed(1) || 'N/A'} veh/hr</p>
                  <p><strong>Congestion Level:</strong> {congestionLevel}</p>
                  {segment.police_control && (
                    <p><strong>Police Control:</strong> Active ({Math.round((1 - segment.police_reduction) * 100)}% flow)</p>
                  )}
                </div>
              </Popup>
            </Polyline>
          );
        }

        // Render intersections as circle markers
        if (segment.segment_type === 'intersection' && segment.coordinates.length > 0) {
          const position = segment.coordinates[0] as LatLngExpression;
          return (
            <CircleMarker
              key={segment.id}
              center={position}
              radius={8}
              fillColor={color}
              color="#ffffff"
              weight={2}
              opacity={opacity}
              fillOpacity={0.8}
              eventHandlers={{
                click: (e) => {
                  e.originalEvent.stopPropagation();
                  onSegmentSelect(segment.id);
                }
              }}
            >
              <Popup>
                <div>
                  <h4>{segment.name}</h4>
                  <p><strong>Type:</strong> Intersection</p>
                  <p><strong>Capacity:</strong> {segment.capacity} veh/hr</p>
                  <p><strong>Current Queue:</strong> {status?.current_queue?.toFixed(1) || 'N/A'} vehicles</p>
                  <p><strong>Current Flow:</strong> {status?.current_flow?.toFixed(1) || 'N/A'} veh/hr</p>
                  <p><strong>Congestion Level:</strong> {congestionLevel}</p>
                  <p><strong>Cycle Time:</strong> {segment.cycle_time}s</p>
                  <p><strong>Green Time:</strong> {(segment.green_time || 0) + segment.green_time_adjustment}s</p>
                  {segment.green_time_adjustment !== 0 && (
                    <p><strong>Green Time Adjustment:</strong> +{segment.green_time_adjustment}s</p>
                  )}
                </div>
              </Popup>
            </CircleMarker>
          );
        }

        return null;
      })}
    </MapContainer>
  );
};

export default TrafficMap;