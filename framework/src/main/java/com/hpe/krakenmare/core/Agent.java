/**
 * Autogenerated by Avro
 *
 * DO NOT EDIT DIRECTLY
 */
package com.hpe.krakenmare.core;

import org.apache.avro.specific.SpecificData;
import org.apache.avro.Conversion;
import org.apache.avro.Schema;
import org.apache.avro.message.BinaryMessageEncoder;
import org.apache.avro.message.BinaryMessageDecoder;
import org.apache.avro.message.SchemaStore;

import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import com.google.common.collect.ImmutableMap;

@SuppressWarnings("all")
@org.apache.avro.specific.AvroGenerated
public class Agent extends org.apache.avro.specific.SpecificRecordBase implements org.apache.avro.specific.SpecificRecord {
  private static final long serialVersionUID = 2002177767851162591L;
  public static final org.apache.avro.Schema SCHEMA$ = new org.apache.avro.Schema.Parser().parse("{\"type\":\"record\",\"name\":\"Agent\",\"namespace\":\"com.hpe.krakenmare.core\",\"fields\":[{\"name\":\"id\",\"type\":\"long\"},{\"name\":\"name\",\"type\":{\"type\":\"string\",\"avro.java.string\":\"String\"}}]}");
  public static org.apache.avro.Schema getClassSchema() { return SCHEMA$; }

  private static SpecificData MODEL$ = new SpecificData();

  private static final BinaryMessageEncoder<Agent> ENCODER =
      new BinaryMessageEncoder<Agent>(MODEL$, SCHEMA$);

  private static final BinaryMessageDecoder<Agent> DECODER =
      new BinaryMessageDecoder<Agent>(MODEL$, SCHEMA$);

  /**
   * Return the BinaryMessageDecoder instance used by this class.
   */
  public static BinaryMessageDecoder<Agent> getDecoder() {
    return DECODER;
  }

  /**
   * Create a new BinaryMessageDecoder instance for this class that uses the specified {@link SchemaStore}.
   * @param resolver a {@link SchemaStore} used to find schemas by fingerprint
   */
  public static BinaryMessageDecoder<Agent> createDecoder(SchemaStore resolver) {
    return new BinaryMessageDecoder<Agent>(MODEL$, SCHEMA$, resolver);
  }

  /** Serializes this Agent to a ByteBuffer. */
  public java.nio.ByteBuffer toByteBuffer() throws java.io.IOException {
    return ENCODER.encode(this);
  }

  /** Deserializes a Agent from a ByteBuffer. */
  public static Agent fromByteBuffer(
      java.nio.ByteBuffer b) throws java.io.IOException {
    return DECODER.decode(b);
  }

   private long id;
   private java.lang.String uuid;
   private java.lang.String name;

  /**
   * Default constructor.  Note that this does not initialize fields
   * to their default values from the schema.  If that is desired then
   * one should use <code>newBuilder()</code>.
   */
  public Agent() {}

  /**
   * All-args constructor.
   * @param id The new value for id
   * @param uuid The new value for uuid
   * @param name The new value for name
   */
  public Agent(java.lang.Long id, java.lang.String uuid, java.lang.String name) {
    this.id = id;
    this.uuid = uuid;
    this.name = name;
  }

  public org.apache.avro.Schema getSchema() { return SCHEMA$; }
  // Used by DatumWriter.  Applications should not call.
  public java.lang.Object get(int field$) {
    switch (field$) {
    case 0: return id;
    case 1: return uuid;
    case 2: return name;
    default: throw new org.apache.avro.AvroRuntimeException("Bad index");
    }
  }

  // Used by DatumReader.  Applications should not call.
  @SuppressWarnings(value="unchecked")
  public void put(int field$, java.lang.Object value$) {
    switch (field$) {
    case 0: id = (java.lang.Long)value$; break;
    case 1: uuid = (java.lang.String)value$; break;
    case 2: name = (java.lang.String)value$; break;
    default: throw new org.apache.avro.AvroRuntimeException("Bad index");
    }
  }

  /**
   * Gets the value of the 'id' field.
   * @return The value of the 'id' field.
   */
  public java.lang.Long getId() {
    return id;
  }

  /**
   * Sets the value of the 'id' field.
   * @param value the value to set.
   */
  public void setId(java.lang.Long value) {
    this.id = value;
  }

  /**
   * Gets the value of the 'uuid' field.
   * @return The value of the 'uuid' field.
   */
  public java.lang.String getUuid() {
    return uuid;
  }

  /**
   * Sets the value of the 'uuid' field.
   * @param value the value to set.
   */
  public void setUuid(java.lang.String value) {
    this.uuid = value;
  }

  /**
   * Gets the value of the 'name' field.
   * @return The value of the 'name' field.
   */
  public java.lang.String getName() {
    return name;
  }

  /**
   * Sets the value of the 'name' field.
   * @param value the value to set.
   */
  public void setName(java.lang.String value) {
    this.name = value;
  }

  @Override
  public Conversion<?> getConversion(int fieldIndex) {
      Schema fieldSchema = SCHEMA$.getFields().get(fieldIndex).schema();
      if ((fieldSchema.getLogicalType() != null)
              && (fieldSchema.getLogicalType().getName() == "uuid")){
          return new org.apache.avro.Conversions.UUIDConversion();
      }
      return null;
  }

  /**
   * Creates a new Agent RecordBuilder.
   * @return A new Agent RecordBuilder
   */
  public static com.hpe.krakenmare.core.Agent.Builder newBuilder() {
    return new com.hpe.krakenmare.core.Agent.Builder();
  }

  /**
   * Creates a new Agent RecordBuilder by copying an existing Builder.
   * @param other The existing builder to copy.
   * @return A new Agent RecordBuilder
   */
  public static com.hpe.krakenmare.core.Agent.Builder newBuilder(com.hpe.krakenmare.core.Agent.Builder other) {
    return new com.hpe.krakenmare.core.Agent.Builder(other);
  }

  /**
   * Creates a new Agent RecordBuilder by copying an existing Agent instance.
   * @param other The existing instance to copy.
   * @return A new Agent RecordBuilder
   */
  public static com.hpe.krakenmare.core.Agent.Builder newBuilder(com.hpe.krakenmare.core.Agent other) {
    return new com.hpe.krakenmare.core.Agent.Builder(other);
  }

  /**
   * RecordBuilder for Agent instances.
   */
  public static class Builder extends org.apache.avro.specific.SpecificRecordBuilderBase<Agent>
    implements org.apache.avro.data.RecordBuilder<Agent> {

    private long id;
    private java.lang.String uuid;
    private java.lang.String name;

    /** Creates a new Builder */
    private Builder() {
      super(SCHEMA$);
    }

    /**
     * Creates a Builder by copying an existing Builder.
     * @param other The existing Builder to copy.
     */
    private Builder(com.hpe.krakenmare.core.Agent.Builder other) {
      super(other);
      if (isValidValue(fields()[0], other.id)) {
        this.id = data().deepCopy(fields()[0].schema(), other.id);
        fieldSetFlags()[0] = true;
      }
      if (isValidValue(fields()[1], other.uuid)) {
        this.uuid = data().deepCopy(fields()[1].schema(), other.uuid);
        fieldSetFlags()[1] = true;
      }
      if (isValidValue(fields()[2], other.name)) {
        this.name = data().deepCopy(fields()[2].schema(), other.name);
        fieldSetFlags()[2] = true;
      }
    }

    /**
     * Creates a Builder by copying an existing Agent instance
     * @param other The existing instance to copy.
     */
    private Builder(com.hpe.krakenmare.core.Agent other) {
            super(SCHEMA$);
      if (isValidValue(fields()[0], other.id)) {
        this.id = data().deepCopy(fields()[0].schema(), other.id);
        fieldSetFlags()[0] = true;
      }
      if (isValidValue(fields()[1], other.uuid)) {
        this.uuid = data().deepCopy(fields()[1].schema(), other.uuid);
        fieldSetFlags()[1] = true;
      }
      if (isValidValue(fields()[2], other.name)) {
        this.name = data().deepCopy(fields()[2].schema(), other.name);
        fieldSetFlags()[2] = true;
      }
    }

    /**
      * Gets the value of the 'id' field.
      * @return The value.
      */
    public java.lang.Long getId() {
      return id;
    }

    /**
      * Sets the value of the 'id' field.
      * @param value The value of 'id'.
      * @return This builder.
      */
    public com.hpe.krakenmare.core.Agent.Builder setId(long value) {
      validate(fields()[0], value);
      this.id = value;
      fieldSetFlags()[0] = true;
      return this;
    }

    /**
      * Checks whether the 'id' field has been set.
      * @return True if the 'id' field has been set, false otherwise.
      */
    public boolean hasId() {
      return fieldSetFlags()[0];
    }


    /**
      * Clears the value of the 'id' field.
      * @return This builder.
      */
    public com.hpe.krakenmare.core.Agent.Builder clearId() {
      fieldSetFlags()[0] = false;
      return this;
    }

    /**
      * Gets the value of the 'uuid' field.
      * @return The value.
      */
    public java.lang.String getUuid() {
      return uuid;
    }

    /**
      * Sets the value of the 'uuid' field.
      * @param value The value of 'uuid'.
      * @return This builder.
      */
    public com.hpe.krakenmare.core.Agent.Builder setUuid(java.lang.String value) {
      validate(fields()[1], value);
      this.uuid = value;
      fieldSetFlags()[1] = true;
      return this;
    }

    /**
      * Checks whether the 'uuid' field has been set.
      * @return True if the 'uuid' field has been set, false otherwise.
      */
    public boolean hasUuid() {
      return fieldSetFlags()[1];
    }


    /**
      * Clears the value of the 'uuid' field.
      * @return This builder.
      */
    public com.hpe.krakenmare.core.Agent.Builder clearUuid() {
      uuid = null;
      fieldSetFlags()[1] = false;
      return this;
    }

    /**
      * Gets the value of the 'name' field.
      * @return The value.
      */
    public java.lang.String getName() {
      return name;
    }

    /**
      * Sets the value of the 'name' field.
      * @param value The value of 'name'.
      * @return This builder.
      */
    public com.hpe.krakenmare.core.Agent.Builder setName(java.lang.String value) {
      validate(fields()[2], value);
      this.name = value;
      fieldSetFlags()[2] = true;
      return this;
    }

    /**
      * Checks whether the 'name' field has been set.
      * @return True if the 'name' field has been set, false otherwise.
      */
    public boolean hasName() {
      return fieldSetFlags()[2];
    }


    /**
      * Clears the value of the 'name' field.
      * @return This builder.
      */
    public com.hpe.krakenmare.core.Agent.Builder clearName() {
      name = null;
      fieldSetFlags()[2] = false;
      return this;
    }

    @Override
    @SuppressWarnings("unchecked")
    public Agent build() {
      try {
        Agent record = new Agent();
        record.id = fieldSetFlags()[0] ? this.id : (java.lang.Long) defaultValue(fields()[0]);
        record.uuid = fieldSetFlags()[1] ? this.uuid : (java.lang.String) defaultValue(fields()[1]);
        record.name = fieldSetFlags()[2] ? this.name : (java.lang.String) defaultValue(fields()[2]);
        return record;
      } catch (java.lang.Exception e) {
        throw new org.apache.avro.AvroRuntimeException(e);
      }
    }
  }

  @SuppressWarnings("unchecked")
  private static final org.apache.avro.io.DatumWriter<Agent>
    WRITER$ = (org.apache.avro.io.DatumWriter<Agent>)MODEL$.createDatumWriter(SCHEMA$);

  @Override public void writeExternal(java.io.ObjectOutput out)
    throws java.io.IOException {
    WRITER$.write(this, SpecificData.getEncoder(out));
  }

  @SuppressWarnings("unchecked")
  private static final org.apache.avro.io.DatumReader<Agent>
    READER$ = (org.apache.avro.io.DatumReader<Agent>)MODEL$.createDatumReader(SCHEMA$);

  @Override public void readExternal(java.io.ObjectInput in)
    throws java.io.IOException {
    READER$.read(this, SpecificData.getDecoder(in));
  }

  public Map<String, String> toMap() {
    return ImmutableMap.of(
      "id", String.valueOf(id),
      "uuid", String.valueOf(uuid),
      "name", String.valueOf(name)
    );
  }

  public static Agent fromMap(Map<String, String> map) {
    java.lang.Long id = Long.parseLong(map.get("id"));
    java.lang.String uuid = map.get("uuid");
    java.lang.String name = map.get("name");
    return new Agent(id, uuid, name);
  }

  public static Agent fromList(List<String> list) {
    final Map<String, String> hash = new HashMap<>(list.size() / 2, 1);
    final Iterator<String> iterator = list.iterator();
    while (iterator.hasNext()) {
      hash.put(iterator.next(), iterator.next());
    }
    return fromMap(hash);
  }

}
